from mastodon import Mastodon
from mastodon.Mastodon import MastodonAPIError
from PyQt5.QtCore import QObject, QSettings


class DataManager(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mastodon = None
        self.instance_host = ''
        self.client_id = ''
        self.client_secret = ''
        self.access_token = ''
        self.refresh_token = ''

    def load_settings(self):
        self._settings = QSettings("NixieCraft", "TootApp")

        self.instance_host = self._settings.value("core/instance_host", "")
        self.client_id = self._settings.value("core/client_id", "")
        self.client_secret = self._settings.value("core/client_secret", "")
        self.access_token = self._settings.value("core/access_token", "")
        self.refresh_token = self._settings.value("core/refresh_token", "")

        if self.access_token:
            self.mastodon = Mastodon(self.client_id, client_secret=self.client_secret, access_token=self.access_token, api_base_url=self.instance_host)

    def save_settings(self):
        self._settings.setValue("core/instance_host", self.instance_host)
        self._settings.setValue("core/client_id", self.client_id)
        self._settings.setValue("core/client_secret", self.client_secret)
        self._settings.setValue("core/access_token", self.access_token)

    def register_instance(self, instance_host):
        self.instance_host = instance_host

        client_id, client_secret = Mastodon.create_app(
            'TootTest',
            api_base_url=instance_host,
        )

        self.client_id = client_id
        self.client_secret = client_secret
        self.mastodon = Mastodon(self.client_id, client_secret=self.client_secret, api_base_url=self.instance_host)

        self.save_settings()

        return True

    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token
        # self.mastodon = Mastodon(self.client_id, client_secret=self.client_secret, access_token=self.access_token, api_base_url=self.instance_host)

        self.save_settings()

    def login(self):
        self.access_token = self.mastodon.log_in(code=self.refresh_token)
        self.mastodon = Mastodon(self.client_id, client_secret=self.client_secret, access_token=self.access_token, api_base_url=self.instance_host)

        self.save_settings()

    def get_auth_request_url(self):
        return self.mastodon.auth_request_url(client_id=self.client_id)
