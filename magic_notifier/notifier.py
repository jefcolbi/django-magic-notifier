from magic_notifier.emailer import Emailer
from magic_notifier.smsers import ExternalSMS
from magic_notifier.pusher import Pusher
import logging
import traceback
from magic_notifier.settings import NOTIFIER_THREADED
from django.contrib.auth import get_user_model
from typing import  Union

User = get_user_model()

logger = logging.getLogger("notifier")


def notify(
    vias: list,
    subject: str = None,
    receivers: Union[str, list] = None,
    template: str = None,
    context: dict = {},
    final_message: str = None,
    smtp_account: str = 'default',
    threaded: bool = None,
):
    logger.info(f"Sending {subject} to {receivers} via {vias}")
    threaded = threaded if threaded is not None else NOTIFIER_THREADED

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
                )
                em.send()

            elif via == "sms":
                ex_sms = ExternalSMS(receivers, template, context, threaded=threaded)
                ex_sms.send()

            elif via == "push":
                pusher = Pusher(
                    subject, receivers, template, context, threaded=threaded
                )
                pusher.send()

            else:
                logger.error(f"Unknown sending method {via}")

        except:
            logger.error(traceback.format_exc())
