from PyQt5 import QtWebEngineWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, QUrl

from tootbox.core.framework import LayoutView


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
            self.on_authenticated.emit(filename)
            self.close()
