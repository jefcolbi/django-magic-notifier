import importlib
import logging
import traceback
from threading import Thread

from django.template.loader import render_to_string

from magic_notifier.models import Notification

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except Exception:
    pass
import json

from django.template import Context, Template

from magic_notifier.utils import NotificationBuilder, get_settings

logger = logging.getLogger("notif")


class Pusher:
    def __init__(
        self, subject, receivers: list, template: str, context: dict,
            push_gateway=None, remove_notification_fields: list=None,
            final_notification: Notification = None,
            inited_by: "User"=None, **kwargs
    ):
        """

        :param subject:The subject of the notification
        :param receivers: The user list of receivers
        :param template: The template to use
        :param context:The context to pass to the template
        :param inited_by: The user who inited the notification
        :param kwargs:
        """
        self.receivers: list = receivers
        self.template: str = template
        self.context: dict = context
        self.remove_notification_fields = remove_notification_fields
        self.final_notification: Notification = final_notification
        self.inited_by = inited_by
        if 'subject' not in context and subject:
            self.context['subject'] = subject
        self.threaded: bool = kwargs.get("threaded", False)
        self.image = kwargs.get("image")
        # get the default sms gateway
        self.push_gateway = get_settings('PUSH::DEFAULT_GATEWAY') if push_gateway is None else push_gateway
        # get the sms gateway definition
        NOTIFIER_PUSH_GATEWAY = get_settings('PUSH')["GATEWAYS"][self.push_gateway]
        # get the sms client to be used
        NOTIFIER_PUSH_CLIENT = NOTIFIER_PUSH_GATEWAY['CLIENT']
        # load the sms client
        module_name, class_name = NOTIFIER_PUSH_CLIENT.rsplit(".", 1)
        module = importlib.import_module(module_name)
        assert hasattr(module, class_name), "class {} is not in {}".format(class_name, module_name)
        self.client_class = getattr(module, class_name)
        self.push_class_options = NOTIFIER_PUSH_GATEWAY

    def send(self):
        if self.threaded:
            t = Thread(target=self._send)
            t.setDaemon(True)
            t.start()
        else:
            return self._send()

    def _send(self):
        try:
            client = self.client_class()

            for user in self.receivers:
                logger.debug(f"sending push notification to {user}")
                if self.final_notification:
                    notification = self.final_notification
                else:
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
                        .inited_by(self.inited_by)
                    )

                    if self.image:
                        not_builder.image(self.image)

                    notification = not_builder.save()

                client.send(user, notification, self.push_class_options,
                                  remove_notification_fields=self.remove_notification_fields)
                # event['id'] = res.id
                #
                # # return
                # channel_layer = get_channel_layer()
                # async_to_sync(channel_layer.group_send)(
                #     f"user-{user.id}",
                #     event
                # )

                return notification
        except Exception as e:
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    pass
