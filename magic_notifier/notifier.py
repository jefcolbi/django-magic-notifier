import logging
import traceback
from typing import Optional, Union

from django.contrib.auth import get_user_model
from django.db import models

from magic_notifier.emailer import Emailer
from magic_notifier.pusher import Pusher
from magic_notifier.settings import NOTIFIER_THREADED
from magic_notifier.smser import ExternalSMS

User = get_user_model()

logger = logging.getLogger("notifier")


def notify(
    vias: list,
    subject: str = None,
    receivers: Union[str, list, models.QuerySet, models.Manager] = None,
    template: str = None,
    context: dict = {},
    final_message: str = None,
    smtp_account: str = 'default',
    sms_gateway: Optional[str] = None,
    files: list = None,
    threaded: bool = None,
):
    """Send a notification

    :param vias: list of sendin method. can be email|sms|push
    :param subject: the subject of the notification
    :param receivers: the receivers list. can be a list of user instances or a string representing users like admins|staff|all|all-staff|all-admins
    :param template: the email template. ignored if final message is passed
    :param context: the context
    :param final_message: the direct content of the notification
    :param smtp_account: the smtp account to use
    :param threaded: if the notification must be send via a worker thread
    :return:
    """
    logger.debug(f"Sending {subject} to {receivers} via {vias}")
    threaded = threaded if threaded is not None else NOTIFIER_THREADED

    assert subject, "subject not defined"


    if isinstance(receivers, str) and receivers in ["admins", "staff", "all", "all-staff", "all-admins"]:
        if receivers == "admins":
            receivers = User.objects.filter(is_superuser=True)
        elif receivers == "staff":
            receivers = User.objects.filter(is_staff=True)
        elif receivers == "all":
            receivers = User.objects.all()
        elif receivers == "all-staff":
            receivers = User.objects.exclude(is_staff=True)
        elif receivers == "all-admins":
            receivers = User.objects.exclude(is_superuser=True)
        else:
            raise ValueError(f"'{receivers}' is not an allowed value for receivers arguments")

    assert isinstance(receivers, (list, models.Manager, models.QuerySet)), f"receivers must be a list at this point not {receivers}"

    for via in vias:
        try:
            if via == "email":
                em = Emailer(
                    subject,
                    receivers,
                    template,
                    context,
                    smtp_account,
                    threaded=threaded,
                    final_message=final_message,
                    files=files
                )
                em.send()

            elif via == "sms":
                ex_sms = ExternalSMS(receivers,context, threaded=threaded,
                    template=template, final_message=final_message,
                    sms_gateway=sms_gateway)
                ex_sms.send()

            elif via == "push":
                assert template, "template variable can't be None or empty"

                pusher = Pusher(
                    subject, receivers, template, context, threaded=threaded
                )
                pusher.send()

            else:
                logger.error(f"Unknown sending method {via}")

        except:
            logger.error(traceback.format_exc())
