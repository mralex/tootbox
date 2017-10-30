from PyQt5 import QtWidgets


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
