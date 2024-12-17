import requests
from django.conf import settings
import logging
import time
from random import randint

logger = logging.getLogger("notifier")

class WahaClient:

    @classmethod
    def send(cls, number: str, text: str, **kwargs):
        session = requests.Session()

        wa_number = number.replace('+', '') + "@c.us"

        base_url = kwargs["BASE_URL"]
        url_check_number = f"{base_url}/api/contacts/check-exists"
        url_send_typing = f"{base_url}/api/startTyping"
        url_stop_typing = f"{base_url}/api/stopTyping"
        url_send_message = f"{base_url}/api/sendText"

        logger.info(f"Checking if {wa_number} exists")
        resp = session.get(url_check_number, params={'phone': wa_number, 'session': 'default'})
        logger.info(f"{resp.content = }")
        res = resp.json()
        if not res['numberExists']:
            logger.info(f"Number {number} doesn't exist aborting")
            return

        wa_number = res['chatId']

        logger.info(f"Start typing to {wa_number}")
        resp = session.post(url_send_typing, json={'chatId': wa_number, 'session': 'default'})
        logger.info(f"{resp.content = }")
        time.sleep(randint(5, 10))

        logger.info(f"Stop typing to {wa_number}")
        resp = session.post(url_stop_typing, json={'chatId': wa_number, 'session': 'default'})
        logger.info(f"{resp.content = }")

        logger.info(f"Send message to {wa_number}")
        resp = session.post(url_send_message, json={'chatId': wa_number, 'session': 'default',
                                                    'text': text})
        logger.info(f"{resp.content = }")
