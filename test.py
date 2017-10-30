import datetime
import json
import re
import sys

from mastodon import Mastodon
from mastodon.Mastodon import MastodonAPIError
from PyQt5 import QtWidgets, QtGui, QtWebEngineWidgets
from PyQt5.QtCore import pyqtSignal, QUrl, QObject, QSettings
import requests


instance_host = "http://mastodev.local:3000"
secrets = {
    "client_id": "bf147bbe4e4c1e42254513d70f53637688cd6ae88185c24d4c46765a48014967",
    "client_secret": "f9456f96fbfac4de7716e6b52cfdc7b0e344bc1a4f94af14d1fd8204d3dbf969",
    "access_token": "0506a19ecccfc69f039bda916bf0cc73392848c8986deb90eec4ceb3a7887747",
}

def prettydate(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(round(diff.days))
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(round(s))
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(round(s/60))
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(round(s/3600))


class Controller(QObject):
    view_class = None

    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = application
        self.register_view()

    def get_view_class(self):
        if self.view_class is None:
            raise Exception("Controller requires a view_class or an implementation of get_view_class()")
        else:
            return self.view_class

    def initialize_view(self):
        view = self.get_view_class()(self)
        # import ipdb ; ipdb.set_trace()
        return view

    def configure_view(self):
        pass

    def register_view(self):
        self.view = self.initialize_view()
        self.configure_view()
        self.view_window_index = self.app.window.add_view(self.view)


class View(QtWidgets.QWidget):
    def __init__(self, controller, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)

        self.controller = controller

class LayoutView(View):
    pass


# Possibly want something like flux?
class DataManager(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mastodon = None
        self.instance_host = ''
        self.client_id = ''
        self.client_secret = ''
        self.access_token = ''

    def load_settings(self):
        self._settings = QSettings("NixieCraft", "TootApp")

        self.instance_host = self._settings.value("core/instance_host", "")
        self.client_id = self._settings.value("core/client_id", "")
        self.client_secret = self._settings.value("core/client_secret", "")
        self.access_token = self._settings.value("core/access_token", "")

    def register_instance(self, instance_host):
        self.instance_host = instance_host

        client_id, client_secret = Mastodon.create_app(
            'TootTest',
            api_base_url=instance_host,
        )

        self.client_id = client_id
        self.client_secret = client_secret

        # XXX Need to define access token on Mastodon object.....
        self.mastodon = Mastodon(self.client_id, client_secret=self.client_secret, api_base_url=instance_host)

        return True

    def get_auth_request_url(self):
        return self.mastodon.auth_request_url(client_id=self.client_id)

class ClickableLabel(QtWidgets.QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, e):
        self.clicked.emit()


class TootContent(QtWidgets.QWidget):
    def __init__(self, toot):
        super().__init__()

        self.toot = toot
        self.displaying_content = True

        self.initialize_ui()

    def initialize_ui(self):
        self.toot_text = QtWidgets.QLabel()
        self.toot_text.setWordWrap(True)
        self.toot_text.setOpenExternalLinks(True)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        if self.toot["sensitive"]:
            self.displaying_content = False
            self.content_warning_button = QtWidgets.QPushButton(self.toot["spoiler_text"])
            self.content_warning_button.clicked.connect(self.warning_clicked)
            vbox.addWidget(self.content_warning_button)
        else:
            self.toot_text.setText(self.toot["content"])

        vbox.addWidget(self.toot_text)

        self.setLayout(vbox)

    def warning_clicked(self):
        self.displaying_content = not self.displaying_content

        text = ""
        if self.displaying_content:
            text = self.toot["content"]

        self.toot_text.setText(text)

class Toot(QtWidgets.QWidget):
    def __init__(self, toot):
        super().__init__()

        self.toot = toot

        self.initialize_ui()

    def initialize_ui(self):
        self.author_label = ClickableLabel(self.toot["account"]["display_name"])
        self.author_label.clicked.connect(lambda: print("Author label clicked"))

        font = self.author_label.font()
        font.setWeight(QtGui.QFont.Bold)
        self.author_label.setFont(font)

        self.username_label = ClickableLabel("@" + self.toot["account"]["username"])
        self.username_label.clicked.connect(lambda: print("Author label clicked"))

        self.posted_label = QtWidgets.QLabel(prettydate(self.toot["created_at"].replace(tzinfo=None)))

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.author_label)
        hbox.addWidget(self.username_label)
        hbox.addStretch()
        hbox.addWidget(self.posted_label)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)
        vbox.addWidget(TootContent(self.toot))

        self.setLayout(vbox)


class Timeline(LayoutView):
    def __init__(self):
        super().__init__()

        self.initialize_ui()

    def initialize_ui(self):
        self.button = QtWidgets.QPushButton("Refresh!")

        self.toot_list = QtWidgets.QVBoxLayout()
        self.toot_list.setContentsMargins(0, 0, 0, 0)
        self.toot_list.setSpacing(20)
        self.toot_list.addStretch()

        scrollbox = QtWidgets.QScrollArea()
        scrollbox.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        scrollbox.setFrameStyle(0)
        scrollbox.setWidgetResizable(True)

        scrollContainer = QtWidgets.QWidget()
        scrollContainer.setLayout(self.toot_list)
        scrollbox.setWidget(scrollContainer)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.button)
        vbox.addWidget(scrollbox)

        self.setLayout(vbox)

    def update_list(self, toots):
        for toot in reversed(toots):
            # print(toot.__str__() + "\n\n\n")
            t = Toot(toot)
            self.toot_list.insertWidget(0, t)


class InstanceLogin(LayoutView):
    clicked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch()

        self.instance_input = QtWidgets.QLineEdit()
        self.instance_input.setPlaceholderText("Instance URL")

        self.login_button = QtWidgets.QPushButton("Log in to instance")
        self.login_button.clicked.connect(self.on_login_clicked)

        vbox.addWidget(self.instance_input)
        vbox.addWidget(self.login_button)

        vbox.addStretch()

        self.setLayout(vbox)

    def on_login_clicked(self):
        if self.instance_input.text():
            self.clicked.emit(self.instance_input.text())


class AuthController(Controller):
    view_class = InstanceLogin

    def configure_view(self):
        self.view.clicked.connect(self.on_login_clicked)

    def on_login_clicked(self, instance_host):
        if self.app.data.register_instance(instance_host):
            # We're connected to the instance, display login window
            login_window = LoginWindow(self.app.data.get_auth_request_url())
            login_window.on_authenticated.connect(self.user_logged_in)
            login_window.show()

    def user_logged_in(self, access_token):
        self.app.data.access_token = access_token

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initialize_ui()

    def initialize_ui(self):
        # self.timeline = InstanceLogin()
        #
        # vbox = QtWidgets.QVBoxLayout()
        # vbox.setContentsMargins(0, 0, 0, 0)
        # vbox.addWidget(self.timeline)

        self.container_layout = QtWidgets.QStackedLayout()

        self.setLayout(self.container_layout)
        self.setWindowTitle("TootTest")
        self.setMinimumSize(300, 200)
        self.resize(300, 600)

    def set_router(self, router):
        self.router = router

    def add_view(self, view):
        self.container_layout.addWidget(view)

        return self.container_layout.count() - 1

    def route_to_index(self, index):
        self.container_layout.setCurrentIndex(index)


class LoginWindow(QtWidgets.QWidget):

    on_authenticated = pyqtSignal(str)

    def __init__(self, auth_url):
        super().__init__()

        self.setWindowTitle("Mastodon Login")
        self.setMinimumSize(400, 400)
        self.resize(400, 400)

        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.browser.load(QUrl(auth_url))
        self.browser.urlChanged.connect(self.url_changed)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)

    def url_changed(self, url):
        filename = url.fileName()

        # is the filename in the url a sha hash?
        r = re.compile(r"^[0-9a-f]{64}$")
        if r.search(filename):
            print("Received access token: " + filename)
            self.on_authenticated.emit(filename)
            self.close()


class AppRouter(QObject):
    def __init__(self, application):
        super().__init__()

        self.routes = {}
        self.active_controller = ""

        self.app = application
        self.window = application.window
        self.window.set_router(self)

    def route_to(self, route_name):
        if not self.routes[route_name]["stack_index"]:
            # First time requesting this route, initialize view
            controller_class = self.routes[route_name]["controller_class"]

            # creates controller, instantiates view, and adds to the window.
            # XXX: maybe too much?
            controller = controller_class(self.app)

            self.routes[route_name]["stack_index"] = controller.view_window_index
            self.routes[route_name]["controller"] = controller

        self.window.route_to_index(self.routes[route_name]["stack_index"])

    def register_route(self, name, controller_class):
        self.routes[name] = {
            "stack_index": None,
            "controller_class": controller_class,
            "controller": None,
        }


class Application(QObject):
    def __init__(self):
        super().__init__()

        self.app = QtWidgets.QApplication(sys.argv)

        self.window = Window()
        self.data = DataManager()
        self.router = AppRouter(self)

        self.register_routes()

    def start(self):
        self.data.load_settings()

        if not self.data.access_token:
            self.router.route_to("login")
        else:
            # TODO: Go straight to timeline if we have an access_token
            pass

        self.window.show()
        sys.exit(self.app.exec_())

    def register_routes(self):
        self.router.register_route("login", AuthController)
        self.router.register_route("timelines/home", Timeline)
        self.router.register_route("timelines/local", Timeline)
        self.router.register_route("timelines/federation", Timeline)
        self.router.register_route("notifications", Timeline)


if __name__ == "__main__":
    app = Application()
    app.start()

    # app = QtWidgets.QApplication(sys.argv)
    # w = Window()
    #
    # w.show()
    #
    # m = Mastodon(secrets["client_id"], client_secret=secrets["client_secret"], access_token=secrets["access_token"], api_base_url=instance_host)
    #
    # # print(m.auth_request_url(client_id=secrets["client_id"]))
    # # w.show_login_window(m.auth_request_url(client_id=secrets["client_id"]))
    #
    # # try:
    # #     print(m.account_verify_credentials())
    # #     w.timeline.update_list(m.timeline_home())
    # # except MastodonAPIError as e:
    # #     print("error" + e.__str__())
    #
    # sys.exit(app.exec_())







# # step 1: register app
# register_payload = {
#     "client_name": "PyTest1",
#     "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
# 	"scopes": "read,write,follow"
# }
#
# r = requests.post(instance_host + "/api/v1/apps", data=register_payload)
# json_res = json.loads(r.text)
#
# print("client id: " + json_res['client_id'])
# print("client secret: " + json_res['client_secret'])

# client_id, client_secret = Mastodon.create_app(
#     'PyTest1',
#     api_base_url=instance_host,
# )
#
# print("client id: " + client_id)
# print("client secret: " + client_secret)
#
# mastodon = Mastodon(client_id, client_secret=client_secret, api_base_url=instance_host)
# access_token = mastodon.log_in('alex@redprocess.com', 'helloworld')
# print("access_token: " + access_token)
#
# m = Mastodon(client_id, client_secret=client_secret, access_token=access_token, api_base_url=instance_host)
# print(m.account_verify_credentials())
# print("\n\n-----\n\n")
# print(m.timeline_home())
#
# print(m.toot("Hello from Python!"))
