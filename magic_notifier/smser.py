import importlib
import logging
import traceback
from threading import Thread
from typing import Optional

from django.template.loader import render_to_string

from magic_notifier.utils import get_settings, import_attribute

logger = logging.getLogger("notifier")


class ExternalSMS:

    def __init__(self, receivers: list, context: dict, template: Optional[str]=None,
        final_message: Optional[str]=None, sms_gateway: Optional[str]=None, **kwargs):
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context
        self.threaded: bool = kwargs.get("threaded", False)
        self.final_message: Optional[str] = final_message
        self.sms_gateway = get_settings("NOTIFIER_SMS_DEFAULT_GATEWAY") if sms_gateway is None else sms_gateway

        NOTIFIER_SMS_GATEWAY = get_settings("NOTIFIER_SMS_GATEWAYS")[self.sms_gateway]
        NOTIFIER_SMS_CLIENT = NOTIFIER_SMS_GATEWAY["CLIENT"]

        module_name, class_name = NOTIFIER_SMS_CLIENT.rsplit(".", 1)
        module = importlib.import_module(module_name)
        assert hasattr(module, class_name), "class {} is not in {}".format(class_name, module_name)
        self.client_class = getattr(module, class_name)

    def send(self):
        if self.threaded:
            t = Thread(target=self._send)
            t.setDaemon(True)
            t.start()
        else:
            self._send()

    def _send(self):
        get_user_number = import_attribute(get_settings("NOTIFIER_GET_USER_NUMBER"))

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
                    sms_content = render_to_string("{}/sms.txt".format(self.template), ctx)

                self.client_class.send(number, sms_content)
        except:
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    pass
