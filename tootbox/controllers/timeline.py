from mastodon.Mastodon import MastodonAPIError

from tootbox.core.framework import Controller
from tootbox.views.timeline import Timeline


class TimelineController(Controller):
    view_class = Timeline

    def view_added(self):
        try:
            # print(m.account_verify_credentials())
            self.view.update_list(self.app.data.mastodon.timeline_home())
        except MastodonAPIError as e:
            print("error " + e.__str__())
