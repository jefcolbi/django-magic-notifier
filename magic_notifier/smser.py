import importlib
import logging
import traceback
from threading import Thread
from typing import Optional

from django.conf import settings
from django.template.loader import render_to_string

from magic_notifier.utils import get_settings, import_attribute

logger = logging.getLogger("notifier")


class ExternalSMS:

    def __init__(self, receivers: list, context: dict, template: Optional[str] = None,
                 final_message: Optional[str] = None, sms_gateway: Optional[str] = None, **kwargs):
        """This class is reponsible of sending a notification via sms.

        :param receivers: list of User
        :param template: the name of the template to user. Default None
        :param context: the context to be passed to template. Default None
        :param final_message: the final message to be sent as the notification content, must be sent if template is None, template is ignored if it is sent. Default None
        :param sms_gateway: the sms gateway to use. Default to None
        :param kwargs:
        """
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context
        self.threaded: bool = kwargs.get("threaded", False)
        self.final_message: Optional[str] = final_message
        # get the default sms gateway
        self.sms_gateway = get_settings('SMS::DEFAULT_GATEWAY') if sms_gateway is None else sms_gateway
        # get the sms gateway definition
        NOTIFIER_SMS_GATEWAY = get_settings('SMS')["GATEWAYS"][self.sms_gateway]
        # get the sms client to be used
        NOTIFIER_SMS_CLIENT = NOTIFIER_SMS_GATEWAY['CLIENT']
        # load the sms client
        module_name, class_name = NOTIFIER_SMS_CLIENT.rsplit(".", 1)
        module = importlib.import_module(module_name)
        assert hasattr(module, class_name), "class {} is not in {}".format(class_name, module_name)
        self.client_class = getattr(module, class_name)
        self.sms_class_options = NOTIFIER_SMS_GATEWAY

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
                    sms_content = self.final_message
                else:
                    sms_content = render_to_string("notifier/{}/sms.txt".format(self.template), ctx)

                self.client_class.send(number, sms_content, **self.sms_class_options)
        except:
            logger.error(traceback.format_exc())
