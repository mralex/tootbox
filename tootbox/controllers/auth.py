from tootbox.core.framework import Controller
from tootbox.views.auth import InstanceLogin, LoginWindow


class AuthController(Controller):
    view_class = InstanceLogin

    def configure_view(self):
        self.view.clicked.connect(self.on_login_clicked)

    def on_login_clicked(self, instance_host):
        if self.app.data.register_instance(instance_host):
            # We're connected to the instance, display login window
            self._login_window = LoginWindow(self.app.data.get_auth_request_url())
            self._login_window.on_authenticated.connect(self.user_logged_in)
            self._login_window.show()

    def user_logged_in(self, refresh_token):
        self.app.data.set_refresh_token(refresh_token)
        self.app.data.login()

        self.app.router.route_to("timelines/home")
