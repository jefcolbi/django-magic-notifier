import logging
import traceback
from threading import Thread

from django.template.loader import render_to_string

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except Exception:
    pass
import json

from django.template import Context, Template

from magic_notifier.utils import NotificationBuilder

logger = logging.getLogger("notif")


class Pusher:
    def __init__(
        self, subject, receivers: list, template: str, context: dict, **kwargs
    ):
        """

        :param subject:The subject of the notification
        :param receivers: The user list of receivers
        :param template: The template to use
        :param context:The context to pass to the template
        :param kwargs:
        """
        self.receivers: list = receivers
        self.template: str = template
        self.context: dict = context
        if 'subject' not in context and subject:
            self.context['subject'] = subject
        self.threaded: bool = kwargs.get("threaded", False)
        self.image = kwargs.get("image")

    def send(self):
        if self.threaded:
            t = Thread(target=self._send)
            t.setDaemon(True)
            t.start()
        else:
            return self._send()

    def _send(self):
        try:
            for user in self.receivers:
                logger.debug(f"sending push notification to {user}")
                ctx = self.context.copy()
                ctx["user"] = user
                push_content = render_to_string(f"notifier/{self.template}/push.json", ctx)

                event: dict = json.loads(push_content)
                event['type'] = 'notification'

                not_builder = (
                    NotificationBuilder(event["subject"])
                    .text(event['text'])
                    .type(event["type"], event["sub_type"])
                    .link(event["link"])
                    .mode(event["mode"])
                    .data(event["data"])
                    .actions(event["actions"])
                    .user(user)
                )

                if self.image:
                    not_builder.image(self.image)

                res = not_builder.save()
                event['id'] = res.id

                # return
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user-{user.id}",
                    event
                )

                return res
        except Exception as e:
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    pass
