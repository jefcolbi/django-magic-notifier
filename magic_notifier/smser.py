import importlib
import logging
import traceback
from threading import Thread
from typing import Optional

from django.template.loader import render_to_string

from .settings import NOTIFIER_SMS_CLIENT

logger = logging.getLogger("notifier")


class ExternalSMS:

    def __init__(self, receivers: list, context: dict, template: Optional[str]=None, final_message: Optional[str]=None, **kwargs):
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context
        self.threaded: bool = kwargs.get("threaded", False)
        self.final_message: Optional[str] = final_message

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
        try:
            for rec in self.receivers:
                ctx = self.context.copy()
                ctx["user"] = rec
                sms_content = render_to_string("{}/sms.txt".format(self.template), ctx)

                self.client_class.send(rec.number, sms_content)
        except:
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    pass
