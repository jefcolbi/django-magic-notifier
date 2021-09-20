import logging

from django.conf import settings
from twilio.rest import Client

from .base import BaseSmsClient

logger = logging.getLogger("notifier")


class TwilioClient(BaseSmsClient):

    @classmethod
    def send(cls, number: str, text: str, **kwargs):
        account = kwargs["ACCOUNT"]
        token = kwargs["TOKEN"]
        from_number = kwargs["FROM_NUMBER"]
        client = Client(account, token)
        res = client.messages.create(from_=from_number, to=number, body=text)
        return res
