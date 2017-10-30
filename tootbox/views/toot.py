import datetime

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal


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
