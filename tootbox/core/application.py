import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject

from tootbox.core.framework import AppRouter
from tootbox.core.data import DataManager
from tootbox.views.main_window import Window
from tootbox.routes import routes


class Application(QObject):
    def __init__(self):
        super().__init__()

        self.app = QApplication(sys.argv)

        self.window = Window()
        self.data = DataManager()
        self.router = AppRouter(self)

        self.register_routes()

    def start(self):
        self.data.load_settings()

        if not self.data.access_token:
            self.router.route_to("login")
        else:
            self.router.route_to("timelines/home")

        self.window.show()
        sys.exit(self.app.exec_())

    def register_routes(self):
        for route in routes:
            self.router.register_route(route[0], route[1])

        # self.router.register_route("login", AuthController)
        # self.router.register_route("timelines/home", TimelineController)
        # self.router.register_route("timelines/local", Timeline)
        # self.router.register_route("timelines/federation", Timeline)
        # self.router.register_route("notifications", Timeline)
