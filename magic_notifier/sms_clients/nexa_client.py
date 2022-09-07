import logging

import requests
from django.conf import settings

from .base import BaseSmsClient

logger = logging.getLogger("notifier")


class NexaSmsClient(BaseSmsClient):

    @classmethod
    def send(cls, number: str, text: str, **kwargs):
        sub_account = settings.NOTIFIER["SMS"]["GATEWAYS"]["NEXA"]["EMAIL"]
        sub_account_pass = settings.NOTIFIER["SMS"]["GATEWAYS"]["NEXA"]["PASSWORD"]
        senderid = settings.NOTIFIER["SMS"]["GATEWAYS"]["NEXA"]["SENDERID"]
        params = {
            "user": sub_account,
            "password": sub_account_pass,
            "senderid": senderid,
            "sms": text,
            "mobiles": number.replace('+', ''),
        }
        logger.info(f"Sending sms with data {params}")
        res = requests.post("https://smsvas.com/bulk/public/index.php/api/v1/sendsms", json=params)
        if(res.status_code != 200):
            logger.error(f"Failed to send the sms: {res.content}")
        else:
            logger.info(res.content)
        return res
