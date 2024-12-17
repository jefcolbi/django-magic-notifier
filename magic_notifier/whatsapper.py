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


class Whatsapper:

    def __init__(self, receivers: list, context: dict, template: Optional[str] = None,
                 final_message: Optional[str] = None, whatsapp_gateway: Optional[str] = None, **kwargs):
        """This class is reponsible of sending a notification via whatsapp.

        :param receivers: list of User
        :param template: the name of the template to user. Default None
        :param context: the context to be passed to template. Default None
        :param final_message: the final message to be sent as the notification content, must be sent if template is None, template is ignored if it is sent. Default None
        :param whatsapp_gateway: the whatsapp gateway to use. Default to None
        :param kwargs:
        """
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context
        self.threaded: bool = kwargs.get("threaded", False)
        self.final_message: Optional[str] = final_message
        # get the default whatsapp gateway
        self.whatsapp_gateway = get_settings('WHATSAPP::DEFAULT_GATEWAY') if whatsapp_gateway is None else whatsapp_gateway
        # get the whatsapp gateway definition
        NOTIFIER_WHATSAPP_GATEWAY = get_settings('WHATSAPP')["GATEWAYS"][self.whatsapp_gateway]
        # get the whatsapp client to be used
        NOTIFIER_WHATSAPP_CLIENT = NOTIFIER_WHATSAPP_GATEWAY.get('CLIENT',
                                                    'magic_notifier.whatsapp_clients.waha_client.WahaClient')
        # load the whatsapp client
        module_name, class_name = NOTIFIER_WHATSAPP_CLIENT.rsplit(".", 1)
        module = importlib.import_module(module_name)
        assert hasattr(module, class_name), "class {} is not in {}".format(class_name, module_name)
        self.client_class = getattr(module, class_name)
        self.whatsapp_class_options = NOTIFIER_WHATSAPP_GATEWAY

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
                    whatsapp_content = self.final_message
                else:
                    try:
                        whatsapp_content = render_to_string("notifier/{}/whatsapp.txt".format(self.template), ctx)
                    except TemplateDoesNotExist:
                        whatsapp_content = render_to_string("notifier/{}/sms.txt".format(self.template), ctx)

                self.client_class.send(number, whatsapp_content, **self.whatsapp_class_options)
        except:
            logger.error(traceback.format_exc())
