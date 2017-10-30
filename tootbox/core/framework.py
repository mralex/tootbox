from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject


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

    def view_added(self):
        pass

    def register_view(self):
        self.view = self.initialize_view()
        self.configure_view()
        self.view_window_index = self.app.window.add_view(self.view)
        self.view_added()


class View(QtWidgets.QWidget):
    def __init__(self, controller, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)

        self.controller = controller


class LayoutView(View):
    pass


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
