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
    context: dict = None,
    final_message: str = None,
    email_gateway: str = 'default',
    sms_gateway: Optional[str] = None,
    files: list = None,
    threaded: bool = None,
):
    """This function send a notification via the method specified in parameter vias

    :param vias: accepted values are email,sms,push
    :param subject: the subject of the notification, ignored when send by sms
    :param receivers: it can be a list, queryset or manager of users. if a string is passed it must be *admins* to send to (super) admins, *staff* to send to staff only, *all* to all users, *all-staff* to all users minus staff and *all-admins* to all users excepted admins
    :param template: the name of the template to user. Default None
    :param context: the context to be passed to template. Note that the context is auto-filled with the current the notification is going under the key 'user'. Default None
    :param final_message: the final message to be sent as the notification content, must be sent if template is None, template is ignored if it is sent. Default None
    :param email_gateway: the email gateway to use. Default 'default'
    :param sms_gateway: the sms gateway to use. Default to None
    :param files: list of files to be sent. accept file-like objects, tuple, file path. Default None
    :param threaded: if True, the notification is sent in background else sent with the current thread. Default to NOTIFIER["THREADED"] settings
    :return:
    """
    logger.debug(f"Sending {subject} to {receivers} via {vias}")
    threaded = threaded if threaded is not None else NOTIFIER_THREADED
    context = {} if context is None else context

    assert subject, "subject not defined"


    if isinstance(receivers, str):
        if receivers in ["admins", "staff", "all", "all-staff", "all-admins"]:
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
                    list(receivers),
                    template,
                    context,
                    email_gateway,
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
