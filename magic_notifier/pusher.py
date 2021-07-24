import logging
import traceback
from threading import Thread

from django.template.loader import render_to_string

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except:
    pass
import json

from django.template import Context, Template

from magic_notifier.utils import NotificationBuilder

logger = logging.getLogger("notif")


class Pusher:
    def __init__(
        self, subject, receivers: list, template: str, context: dict, **kwargs
    ):
        self.receivers: list = receivers
        self.template: str = template
        self.context: dict = context
        self.threaded: bool = kwargs.get("threaded", False)
        self.image = kwargs.get("image")

    def send(self):
        if self.threaded:
            t = Thread(target=self._send)
            t.setDaemon(True)
            t.start()
        else:
            self._send()

    def _send(self):
        try:
            for user in self.receivers:
                ctx = self.context.copy()
                ctx["user"] = user
                data_str = json.dumps(ctx.get("data", {}), indent=4)
                ctx["data"] = data_str
                push_content = render_to_string(
                    "{}/push.json".format(self.template), ctx
                )

                print(push_content)

                event: dict = json.loads(push_content)
                print(event)

                not_builder = (
                    NotificationBuilder(event["text"])
                    .type(event["type"], event["sub_type"])
                    .link(event["link"])
                    .mode(event["mode"])
                    .data(event["data"])
                    .actions(event["actions"])
                    .user(user)
                )

                if self.image:
                    not_builder.image(self.image)

                not_builder.save()

                # return

                push_channel = user.settings.push_channel
                print(f"user is waitin to channel {push_channel}")

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.send)(push_channel, event)
        except:
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    pass
