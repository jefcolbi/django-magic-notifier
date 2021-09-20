import logging

import requests
from django.conf import settings

from .base import BaseSmsClient

logger = logging.getLogger("notifier")


class CGSmsClient(BaseSmsClient):

    @classmethod
    def send(cls, number: str, text: str, **kwargs):
        sub_account = settings.NOTIFIER["SMS"]["GATEWAYS"]["CGS"]["SUB_ACCOUNT"]
        sub_account_pass = settings.NOTIFIER["SMS"]["GATEWAYS"]["CGS"]["SUB_ACCOUNT_PASSWORD"]
        params = {
            "sub_account": sub_account,
            "sub_account_pass": sub_account_pass,
            "action": "send_sms",
            "message": text,
            "recipients": number,
        }
        res = requests.get("http://cheapglobalsms.com/api_v1", params=params)
        return res
