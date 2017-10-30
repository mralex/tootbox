from tootbox.controllers.auth import AuthController
from tootbox.controllers.timeline import TimelineController


routes = [
    ("login", AuthController),
    ("timelines/home", TimelineController),
]
