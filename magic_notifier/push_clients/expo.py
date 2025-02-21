import json

import requests
from pyfcm import FCMNotification
from django.contrib.auth import get_user_model
from magic_notifier.models import Notification
from magic_notifier.utils import import_attribute
import logging

User = get_user_model()

logger = logging.getLogger('notifier')


class ExpoClient:

    def send(self, user: User, notification: Notification, options: dict, remove_notification_fields=None):
        remove_notification_fields = [] if not remove_notification_fields else remove_notification_fields
        fcm_user_tokens = import_attribute(options['GET_TOKENS_FUNCTION'])(user)

        data = notification.data

        for fcm_user_token in fcm_user_tokens:
            logger.info(f"Token: {fcm_user_token} :: Data: {data}")
            self.send_push_notification(fcm_user_token, notification.subject, notification.text, data)

    def send_push_notification(self, token:str, title: str, body: str, data: dict):
        url = 'https://exp.host/--/api/v2/push/send'
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            'to': token,
            'sound': 'default',
            'title': title,
            'body': body,
            'data': data,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info(f'Response from Expo: {response.json()}')

