import logging

from django.conf import settings
from twilio.rest import Client

from .base import BaseSmsClient

logger = logging.getLogger("notifier")


class TwilioClient(BaseSmsClient):

    @classmethod
    def send(cls, number: str, text: str):
        account = settings.NOTIFIER["TWILIO"]["ACCOUNT"]
        token = settings.NOTIFIER["TWILIO"]["TOKEN"]
        from_number = settings.NOTIFIER["TWILIO"]["FROM_NUMBER"]
        client = Client(account, token)
        res = client.messages.create(from_=from_number, to=number, body=text)
        return res
