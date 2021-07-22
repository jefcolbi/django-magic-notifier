from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from threading import Thread
from django.conf import settings
import traceback
import re
import unidecode
import logging
from django.utils.translation import gettext as _
from django.utils.translation import activate
from .utils import import_class
from typing import Optional

logger = logging.getLogger("notifier")


class Emailer:
    def __init__(
        self,
        subject: str,
        receivers: list,
        template: Optional[str],
        context: dict,
        smtp_account: str='default',
        final_message: str = None,
        **kwargs,
    ):
        from magic_notifier.settings import NOTIFIER_SMTP
        self.email_settings:dict = NOTIFIER_SMTP[smtp_account]
        self.email_client = import_class(self.email_settings["CLIENT"])

        self.connection = self.email_client.get_connection(self.email_settings)
        self.subject: str = subject
        self.receivers: list = receivers
        self.template: str = template
        self.context: dict = context if context else {}
        self.final_message = final_message
        self.threaded: bool = kwargs.get("threaded", False)

    def send(self):
        if self.threaded:
            t = Thread(target=self._send)
            t.setDaemon(True)
            t.start()
        else:
            self._send()

    def _send(self):
        try:
            logger.info(f"sending emails to {self.receivers}")
            for user in self.receivers:
                # activate(user.settings.lang)

                ctx = self.context.copy()
                ctx["user"] = user
                logger.info(f"===== user name {user.username}")
                logger.info(ctx)

                if self.template:
                    html_content = render_to_string(
                        "{}/email.html".format(self.template), ctx
                    )  # render with dynamic value
                    logger.info(html_content)

                    text_content = render_to_string(
                    "{}/email.txt".format(self.template), ctx
                    )  # render with dynamic value
                    logger.info(text_content)
                else:
                    html_content = text_content = self.final_message

                msg = EmailMultiAlternatives(
                    self.subject,
                    text_content,
                    self.email_settings["FROM"],
                    [user.email],
                    connection=self.connection,
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
        except:
            logger.error(traceback.format_exc())
            print(traceback.format_exc())


if __name__ == "__main__":
    emailer = Emailer("Reset code", ["jefcolbi@gmail.com"], "reset", {}, "account")
    emailer.send()
