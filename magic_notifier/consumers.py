import binascii
import ctypes
import json
import logging
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from notif.models import Notification
from notif.models_serializers import NotificationSerializer
from rest_framework.authtoken.models import Token

logger = logging.getLogger("notif")


class PushNotifConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token: str = None
        self.user = None

    def connect(self):
        try:
            self.accept()

            self.token = self.scope["url_route"]["kwargs"]["token"]
            db_tok = Token.objects.get(key=self.token)
            self.user = db_tok.user

            self.user.settings.push_channel = self.channel_name
            self.user.settings.save()

            logger.info("Accepted")
        except Exception as e:
            print(traceback.print_exc())
            logging.error(traceback.format_exc())

    def disconnect(self, close_code):
        try:
            self.user.settings.push_channel = None
            self.user.settings.save()
        except Exception as e:
            print(traceback.format_exc())
            logging.error(traceback.format_exc())

    def receive(self, text_data):
        event = json.loads(text_data)
        logger.info("{} >> {}".format(self.user, text_data))

        event_handler = getattr(self, event["type"].lower().replace(".", "_"), None)
        if callable(event_handler):
            event_handler(event)

    def notify(self, data: dict):
        self.send(json.dumps(data))

    def notification(self, data: dict):
        self.send(json.dumps(data))

    def unread(self, event: dict):
        notifs = Notification.objects.filter(user=self.user, read__isnull=True)
        event["count"] = len(notifs)
        event["notifications"] = NotificationSerializer(notifs, many=True).data
        self.send(json.dumps(event))

    def markread(self, event: dict):
        notifs = Notification.objects.filter(user=self.user, read__isnull=True)
        notifs.update(read=timezone.now())
        event["success"] = True
        self.send(json.dumps(event))
