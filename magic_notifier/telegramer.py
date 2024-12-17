import importlib
import logging
import traceback
from threading import Thread
from typing import Optional

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from magic_notifier.utils import get_settings, import_attribute

logger = logging.getLogger("notifier")


class Telegramer:

    def __init__(self, receivers: list, context: dict, template: Optional[str] = None,
                 final_message: Optional[str] = None, telegram_gateway: Optional[str] = None, **kwargs):
        """This class is reponsible of sending a notification via telegram.

        :param receivers: list of User
        :param template: the name of the template to user. Default None
        :param context: the context to be passed to template. Default None
        :param final_message: the final message to be sent as the notification content, must be sent if template is None, template is ignored if it is sent. Default None
        :param telegram_gateway: the telegram gateway to use. Default to None
        :param kwargs:
        """
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context
        self.threaded: bool = kwargs.get("threaded", False)
        self.final_message: Optional[str] = final_message
        # get the default telegram gateway
        self.telegram_gateway = get_settings('TELEGRAM::DEFAULT_GATEWAY') if telegram_gateway is None else telegram_gateway
        # get the telegram gateway definition
        NOTIFIER_TELEGRAM_GATEWAY = get_settings('TELEGRAM')["GATEWAYS"][self.telegram_gateway]
        # get the telegram client to be used
        NOTIFIER_TELEGRAM_CLIENT = NOTIFIER_TELEGRAM_GATEWAY.get('CLIENT',
                                        'magic_notifier.telegram_clients.telethon.TelethonClient')
        # load the telegram client
        module_name, class_name = NOTIFIER_TELEGRAM_CLIENT.rsplit(".", 1)
        module = importlib.import_module(module_name)
        assert hasattr(module, class_name), "class {} is not in {}".format(class_name, module_name)
        self.client_class = getattr(module, class_name)
        self.telegram_class_options = NOTIFIER_TELEGRAM_GATEWAY

    def send(self):
        if self.threaded:
            t = Thread(target=self._send)
            t.setDaemon(True)
            t.start()
        else:
            self._send()

    def _send(self):
        get_user_number = import_attribute(get_settings("GET_USER_NUMBER"))

        try:
            for rec in self.receivers:
                ctx = self.context.copy()
                ctx["user"] = rec
                number = get_user_number(rec)
                if not number:
                    logger.warning(f"Can't find a number for {rec}, ignoring.")

                if self.final_message:
                    telegram_content = self.final_message
                else:
                    try:
                        telegram_content = render_to_string("notifier/{}/telegram.txt".format(self.template), ctx)
                    except TemplateDoesNotExist:
                        telegram_content = render_to_string("notifier/{}/sms.txt".format(self.template), ctx)

                self.client_class.send(number, rec.first_name, rec.last_name,
                            telegram_content, self.telegram_gateway, **self.telegram_class_options)
        except:
            logger.error(traceback.format_exc())
