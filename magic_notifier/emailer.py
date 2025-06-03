import logging
import os.path
import traceback
from argparse import OPTIONAL
from pathlib import Path
from threading import Thread
from typing import Optional, List

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from mjml import mjml2html
from functools import partial
from django.template.engine import Engine

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
            email_gateway: Optional[str] = None,
            final_message: str = None,
            files: list = None,
            tried_gateways: Optional[List[str]] = None,
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
            NOTIFIER_EMAIL_DEFAULT_GATEWAY = NOTIFIER_EMAIL.get('DEFAULT_GATEWAY', 'default')
        except (AttributeError, KeyError):
            from magic_notifier.settings import NOTIFIER_EMAIL, NOTIFIER_EMAIL_DEFAULT_GATEWAY

        self.fallback_gateways = NOTIFIER_EMAIL.get('FALLBACKS', [])
        self.current_gateway = email_gateway if email_gateway else NOTIFIER_EMAIL_DEFAULT_GATEWAY
        self.email_settings: dict = NOTIFIER_EMAIL[self.current_gateway]
        self.email_client = import_attribute(self.email_settings["CLIENT"])

        self.tried_gateways = tried_gateways if tried_gateways else []

        self.connection = self.email_client.get_connection(self.email_settings)
        self.subject: str = subject
        self.receivers: list = receivers
        self.template: Optional[str] = template
        self.context: dict = context if context else {}
        self.final_message = final_message
        self.threaded: bool = kwargs.get("threaded", False)
        self.files: Optional[list] = files
        self.current_engine = Engine.get_default()
        if self.template:
            self.tpl_abs_path = self.current_engine.find_template(f"notifier/{self.template}/email.mjml")[1].name
        else:
            self.tpl_abs_path = None
        logger.info(f"{self.tpl_abs_path = }")

    def mjml_loader(self, dest: str):
        f_res = os.path.abspath(os.path.join(Path(self.tpl_abs_path).parent, dest))
        with open(f_res) as fp:
            res = fp.read()
        return res

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
                        mjml_content = render_to_string(
                            f"notifier/{self.template}/email.mjml", ctx
                        )
                        logger.debug("mjml_content")
                        logger.debug(mjml_content)
                        html_content = mjml2html(mjml_content, include_loader=self.mjml_loader)
                        logger.debug("html_content")
                        logger.debug(html_content)
                    except TemplateDoesNotExist as e:
                        html_content = None

                    if not html_content:
                        try:
                            html_content = render_to_string(
                                f"notifier/{self.template}/email.html", ctx
                            )  # render with dynamic value
                            logger.debug("html_content")
                            logger.debug(html_content)
                        except TemplateDoesNotExist:
                            html_content = None

                    text_content = render_to_string(
                        f"notifier/{self.template}/email.txt", ctx
                    )  # render with dynamic value
                    logger.debug("text_content")
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
                                logger.warning(
                                    f"file {name} can't be added to mail because it is not a file-like object")
                        elif hasattr(pos_file, 'read'):
                            msg.attach(f"file {i + 1}", pos_file.read())
                        else:
                            logger.warning(f"discarding possible file {pos_file}")

                logger.debug(f"Sending email via connection")
                msg.send()
                logger.debug(f"Email sent!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.tried_gateways.append(self.current_gateway)
            if self.fallback_gateways:
                for gateway in self.fallback_gateways:
                    if gateway not in self.tried_gateways:
                        logger.warning(f"We are falling back to {gateway} gateway")
                        new_emailer = Emailer(self.subject, self.receivers, self.template, self.context,
                                              email_gateway=gateway, final_message=self.final_message,
                                              files=self.files, tried_gateways=self.tried_gateways)
                        return new_emailer.send()
