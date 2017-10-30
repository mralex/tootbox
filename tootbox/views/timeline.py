from PyQt5 import QtWebEngineWidgets, QtWidgets

from tootbox.core.framework import LayoutView
from tootbox.views.toot import Toot


class Timeline(LayoutView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_ui()

    def initialize_ui(self):
        self.button = QtWidgets.QPushButton("Refresh!")

        self.toot_list = QtWidgets.QVBoxLayout()
        self.toot_list.setContentsMargins(0, 0, 0, 0)
        self.toot_list.setSpacing(20)
        self.toot_list.addStretch()

        self.scrollbox = QtWidgets.QScrollArea()
        self.scrollbox.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollbox.setFrameStyle(0)
        self.scrollbox.setWidgetResizable(True)

        self.scrollbox.verticalScrollBar().valueChanged.connect(self.timeline_scrolled)

        scrollContainer = QtWidgets.QWidget()
        scrollContainer.setLayout(self.toot_list)
        self.scrollbox.setWidget(scrollContainer)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.button)
        vbox.addWidget(self.scrollbox)

        self.setLayout(vbox)

    def update_list(self, toots):
        for toot in reversed(toots):
            # print(toot.__str__() + "\n\n\n")
            t = Toot(toot)
            self.toot_list.insertWidget(0, t)

    def timeline_scrolled(self, value):
        maximum = self.scrollbox.verticalScrollBar().maximum()
        scroll_perc = value / maximum

        if scroll_perc > 0.9:
            # Request more toots
            pass

        # print(str(value) + ", " + str(maximum) + ", " + str(scroll_perc) + "%")
