import logging
import traceback
from argparse import OPTIONAL
from threading import Thread
from typing import Optional

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from magic_notifier.utils import get_settings

from .utils import import_attribute

logger = logging.getLogger("notifier")


class Emailer:
    def __init__(
        self,
        subject: str,
        receivers: list,
        template: Optional[str],
        context: dict,
        email_gateway: str='default',
        final_message: str = None,
        files: list = None,
        **kwargs,
    ):
        """The class is reponsible of email sending.

        :param subject: the subject of the notification, ignored when send by sms
        :param receivers: list of User
        :param template: the name of the template to user. Default None
        :param context: the context to be passed to template. Default None
        :param email_gateway: the email gateway to use. Default 'default'
        :param final_message: the final message to be sent as the notification content, must be sent if template is None, template is ignored if it is sent. Default None
        :param files: list of files to be sent. accept file-like objects, tuple, file path. Default None
        :param kwargs:
        """
        try:
            NOTIFIER_EMAIL = get_settings('EMAIL')
        except (AttributeError, KeyError):
            from magic_notifier.settings import NOTIFIER_EMAIL
        self.email_settings:dict = NOTIFIER_EMAIL[email_gateway]
        self.email_client = import_attribute(self.email_settings["CLIENT"])

        self.connection = self.email_client.get_connection(self.email_settings)
        self.subject: str = subject
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context if context else {}
        self.final_message = final_message
        self.threaded: bool = kwargs.get("threaded", False)
        self.files: Optional[list] = files

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
                if isinstance(user, str):
                    user = User(email=user, username=user)

                ctx = self.context.copy()
                ctx["user"] = user
                logger.info(f" Sending to user {user.username} with context {ctx}")

                if self.template:
                    try:
                        html_content = render_to_string(
                            f"notifier/{self.template}/email.html", ctx
                        )  # render with dynamic value
                        logger.debug(html_content)
                    except TemplateDoesNotExist:
                        html_content = None

                    text_content = render_to_string(
                    f"notifier/{self.template}/email.txt", ctx
                    )  # render with dynamic value
                    logger.debug(text_content)
                else:
                    html_content = text_content = self.final_message

                msg = EmailMultiAlternatives(
                    self.subject,
                    text_content,
                    self.email_settings["FROM"],
                    [user.email],
                    connection=self.connection,
                )
                if html_content:
                    msg.attach_alternative(html_content, "text/html")

                if self.files:
                    for i, pos_file in enumerate(self.files):
                        if isinstance(pos_file, str):
                            msg.attach_file(pos_file)
                        elif isinstance(pos_file, tuple):
                            name, f = pos_file
                            if hasattr(f, 'read'):
                                msg.attach(name, f.read())
                            else:
                                logger.warning(f"file {name} can't be added to mail because it is not a file-like object")
                        elif hasattr(pos_file, 'read'):
                            msg.attach(f"file {i+1}", pos_file.read())
                        else:
                            logger.warning(f"discarding possible file {pos_file}")
                msg.send()
        except:
            logger.error(traceback.format_exc())
