from magic_notifier.emailer import Emailer
from magic_notifier.smsers import ExternalSMS
from magic_notifier.pusher import Pusher
import logging
import traceback
from magic_notifier.settings import NOTIFIER_THREADED

logger = logging.getLogger("notifier")


def notify(
    vias: list,
    subject: str = None,
    receivers: list = None,
    template: str = None,
    context: dict = {},
    final_message: str = None,
    smtp_account: str = 'default',
    threaded: bool = None,
):
    logger.info(f"Sending {subject} to {receivers} via {vias}")
    threaded = threaded if threaded is not None else NOTIFIER_THREADED

    # TODO: add support to receivers = "admins", "staff", "all", "all-staff", "all-admins"

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
