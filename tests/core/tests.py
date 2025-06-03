import json
import os
import time
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import requests
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import TestCase, override_settings, LiveServerTestCase

from magic_notifier.models import NotifyProfile, Notification
from magic_notifier.notifier import notify
from magic_notifier.pusher import Pusher
from magic_notifier.telegramer import Telegramer
from magic_notifier.telegram_clients.telethon import TelethonClient
from magic_notifier.utils import NotificationBuilder
from magic_notifier.serializers import NotificationSerializer
from magic_notifier.whatsapp_clients.waha_client import WahaClient
from magic_notifier.whatsapper import Whatsapper
User = get_user_model()


class EmailTestCase(TestCase):
    """Class to test emails sending"""

    @classmethod
    def setUpClass(cls):
        User.objects.create(username="user1", email="user1@localhost")
        User.objects.create(username="user2", email="user2@localhost")
        User.objects.create(username="user3", email="user3@localhost")

        User.objects.create(username="user4", email="user4@localhost", is_staff=True)
        User.objects.create(username="user5", email="user5@localhost", is_staff=True)

        User.objects.create(username="user6", email="user6@localhost",
            is_superuser=True, is_staff=True)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        return super().tearDownClass()

    def test_simple_with_user(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], final_message="Nice if you get this")

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)

    def test_simple_with_user_threaded(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], final_message="Nice if you get this",
            threaded=True)
        time.sleep(2)

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)

    def test_simple_direct_email(self):
        subject = "Test magic notifier"
        notify(["email"], subject, ["testuser@localhost"], final_message="Nice if you get this")

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, ["testuser@localhost"])
        self.assertEqual(first_message.subject, subject)

    def test_template_html_txt_with_user(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='base')

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
        self.assertEqual(len(first_message.alternatives), 1)

    def test_template_txt_with_user(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='hello')

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
        self.assertEqual(len(first_message.alternatives), 0)

    def test_template_not_exist_with_user(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='notexist')

        self.assertEqual(len(mail.outbox), 0) # type: ignore

    def test_command_test_email_template(self):
        call_command('test_email_template', 'hello', 'testuser@localhost')

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, ['testuser@localhost'])
        self.assertEqual(first_message.subject, 'Testing email template')
        self.assertEqual(len(first_message.alternatives), 0)

    def test_template_txt_with_user_with_files_filename(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='hello',
            files=[str(Path(__file__).parent / "models.py")])

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
        self.assertEqual(len(first_message.alternatives), 0)
        self.assertGreater(len(first_message.attachments), 0)

    def test_template_txt_with_user_with_files_tuple_string(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='hello',
            files=[("test.txt", "")])

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
        self.assertEqual(len(first_message.alternatives), 0)
        self.assertEqual(len(first_message.attachments), 0) # it failed

    def test_template_txt_with_user_with_files_tuple_filelike(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        with open(str(Path(__file__).parent / "models.py")) as fp:
            notify(["email"], subject, [user], template='hello',
                files=[("models.py", fp)])

            self.assertGreater(len(mail.outbox), 0) # type: ignore
            first_message = mail.outbox[0] # type: ignore
            self.assertEqual(first_message.to, [user.email])
            self.assertEqual(first_message.subject, subject)
            self.assertEqual(len(first_message.alternatives), 0)
            self.assertGreater(len(first_message.attachments), 0)

    def test_template_txt_with_user_with_files_bad(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        with open(str(Path(__file__).parent / "models.py")) as fp:
            notify(["email"], subject, [user], template='hello',
                files=[1])

            self.assertGreater(len(mail.outbox), 0) # type: ignore
            first_message = mail.outbox[0] # type: ignore
            self.assertEqual(first_message.to, [user.email])
            self.assertEqual(first_message.subject, subject)
            self.assertEqual(len(first_message.alternatives), 0)
            self.assertEqual(len(first_message.attachments), 0)

    def test_template_txt_with_user_with_files_filelike(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        with open(str(Path(__file__).parent / "models.py")) as fp:
            notify(["email"], subject, [user], template='hello',
                files=[fp])

            self.assertGreater(len(mail.outbox), 0) # type: ignore
            first_message = mail.outbox[0] # type: ignore
            self.assertEqual(first_message.to, [user.email])
            self.assertEqual(first_message.subject, subject)
            self.assertEqual(len(first_message.alternatives), 0)
            self.assertGreater(len(first_message.attachments), 0)

    def test_simple_with_string_all(self):
        subject = "Test magic notifier"
        notify(["email"], subject, "all", final_message="Nice if you get this")

        self.assertEqual(len(mail.outbox), 6) # type: ignore

    def test_simple_with_string_staff(self):
        subject = "Test magic notifier"
        notify(["email"], subject, "staff", final_message="Nice if you get this")

        self.assertEqual(len(mail.outbox), 3) # type: ignore

    def test_simple_with_string_admins(self):
        subject = "Test magic notifier"
        notify(["email"], subject, "admins", final_message="Nice if you get this")

        self.assertEqual(len(mail.outbox), 1) # type: ignore

    def test_simple_with_string_all_minus_admins(self):
        subject = "Test magic notifier"
        notify(["email"], subject, "all-admins", final_message="Nice if you get this")

        self.assertEqual(len(mail.outbox), 5) # type: ignore

    def test_simple_with_string_all_minius_staff(self):
        subject = "Test magic notifier"
        notify(["email"], subject, "all-staff", final_message="Nice if you get this")

        self.assertEqual(len(mail.outbox), 3) # type: ignore

    def test_simple_with_string_unknown(self):
        subject = "Test magic notifier"
        self.assertRaises(ValueError, notify, ["email"], subject, "unknown", final_message="Nice if you get this")

    def test_unknown_method(self):
        subject = "Test magic notifier"
        notify(["unknown"], subject, "all-staff", final_message="Nice if you get this")
        self.assertEqual(len(mail.outbox), 0) # type: ignore

    def test_amazon_ses(self):
        user = User(email=os.environ['TEST_EMAIL'], username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], final_message="Nice if you get this")

        self.assertGreater(len(mail.outbox), 0)  # type: ignore
        first_message = mail.outbox[0]  # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)


sms_outbox = []

class Sms:

    def __init__(self, number, message):
        self.number = number
        self.message = message

def send_to_sms_outbox(*args, **kwargs):
    print(*args)
    try:
        url = args[-1]
    except:
        url = None
    params = kwargs.get('params')
    data = kwargs.get('data')
    if url:
        if url == 'https://smsvas.com/bulk/public/index.php/api/v1/sendsms':
            data = kwargs['json']
            sms_outbox.append(Sms(data['mobiles'], data['sms']))
            res = requests.Response()
            res.status_code = 200
            return res
        elif url == 'http://cheapglobalsms.com/api_v1':
            params = kwargs['params']
            sms_outbox.append(Sms(params['recipients'], params['message']))
        else:
            sms_outbox.append(Sms(data['To'], data['Body']))
            from twilio.http.response import Response

            return mock.MagicMock(spec=Response, status_code=200,
                text=json.dumps({
                          "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                          "api_version": "2010-04-01",
                          "body": "Hi there",
                          "date_created": "Thu, 30 Jul 2015 20:12:31 +0000",
                          "date_sent": "Thu, 30 Jul 2015 20:12:33 +0000",
                          "date_updated": "Thu, 30 Jul 2015 20:12:33 +0000",
                          "direction": "outbound-api",
                          "error_code": None,
                          "error_message": None,
                          "from": "+15017122661",
                          "messaging_service_sid": "MGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                          "num_media": "0",
                          "num_segments": "1",
                          "price": None,
                          "price_unit": None,
                          "sid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                          "status": "sent",
                          "subresource_uris": {
                            "media": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Media.json"
                          },
                          "to": "+15558675310",
                          "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
                        }))


def notifier_settings_for_global_cheap(*args, **kwargs):
    if args[0] == "SMS::DEFAULT_GATEWAY":
        return "CGS"
    elif args[0] == "SMS":
        return {
                    "GATEWAYS": {
                        "CGS": {
                            "CLIENT": "magic_notifier.sms_clients.cgsms_client.CGSmsClient",
                            "SUB_ACCOUNT": "sub_account",
                            "SUB_ACCOUNT_PASSWORD": "sub_account_password"
                        }
                    }
                }
    elif args[0] == "GET_USER_NUMBER":
        return "magic_notifier.utils.get_user_number"


def notifier_settings_for_nexa(*args, **kwargs):
    if args[0] == "SMS::DEFAULT_GATEWAY":
        return "NEXA"
    elif args[0] == "SMS":
        return {
                    "GATEWAYS": {
                        "NEXA": {
                            "CLIENT": "magic_notifier.sms_clients.nexa_client.NexaSmsClient",
                            "EMAIL": "sub_account",
                            "PASSWORD": "sub_account_password",
                            "SENDERID": "senderid"
                        }
                    }
                }
    elif args[0] == "GET_USER_NUMBER":
        return "magic_notifier.utils.get_user_number"


def notifier_settings_for_twilio(*args, **kwargs):
    if args[0] == "SMS::DEFAULT_GATEWAY":
        return "TWILIO"
    elif args[0] == "SMS":
        return {
                    "GATEWAYS": {
                        "TWILIO": {
                            "CLIENT": "magic_notifier.sms_clients.twilio_client.TwilioClient",
                            "ACCOUNT": "sub_account",
                            "TOKEN": "token",
                            "FROM_NUMBER": "from_number"
                        }
                    }
                }
    elif args[0] == "GET_USER_NUMBER":
        return "magic_notifier.utils.get_user_number"


class SmsTestCase(TestCase):

    @patch('magic_notifier.smser.get_settings', side_effect=notifier_settings_for_global_cheap)
    @patch('magic_notifier.sms_clients.cgsms_client.requests.get', side_effect=send_to_sms_outbox)
    def test_global_cheap_sms_client(self, mock_get_request, mock_get_settings):
        NOTIFIER = {
            "SMS":{
                "GATEWAYS": {
                    "CGS": {
                        "CLIENT": "magic_notifier.sms_clients.cgsms_client.CGSmsClient",
                        "SUB_ACCOUNT": "sub_account",
                        "SUB_ACCOUNT_PASSWORD": "sub_account_password"
                    }
                },
                "DEFAULT_GATEWAY": "CGS"
            }
        }

        with self.settings(NOTIFIER=NOTIFIER):
            user = User.objects.create(email="testuser@localhost", username="testuser")
            not_profile = NotifyProfile.objects.create(phone_number="+237600000000",
                user=user)

            subject = "Test magic notifier"
            notify(["sms"], subject, [user], final_message="Nice if you get this")

            self.assertGreater(len(sms_outbox), 0) # type: ignore
            first_message = sms_outbox[0] # type: ignore
            self.assertEqual(first_message.number, not_profile.phone_number)
            self.assertEqual(first_message.message, "Nice if you get this")

    @patch('magic_notifier.smser.get_settings', side_effect=notifier_settings_for_twilio)
    @patch('twilio.http.http_client.TwilioHttpClient.request', side_effect=send_to_sms_outbox)
    def test_twilio_sms_client(self, mock_get_request, mock_get_settings):
        NOTIFIER = {
            "SMS": {
                "GATEWAYS": {
                    "TWILIO": {
                        "CLIENT": "magic_notifier.sms_clients.twilio_client.TwilioClient",
                        "ACCOUNT": "sub_account",
                        "TOKEN": "token",
                        "FROM_NUMBER": "from_number"
                    }
                },
                "DEFAULT_GATEWAY": "TWILIO"
            }
        }

        with self.settings(NOTIFIER=NOTIFIER):
            user = User.objects.create(email="testuser@localhost", username="testuser")
            not_profile = NotifyProfile.objects.create(phone_number="+237600000000",
                user=user)

            subject = "Test magic notifier"
            notify(["sms"], subject, [user], final_message="Nice if you get this")

            self.assertGreater(len(sms_outbox), 0) # type: ignore
            first_message = sms_outbox[0] # type: ignore
            self.assertEqual(first_message.number, not_profile.phone_number)
            self.assertEqual(first_message.message, "Nice if you get this")

    @patch('magic_notifier.smser.get_settings', side_effect=notifier_settings_for_nexa)
    @patch('magic_notifier.sms_clients.cgsms_client.requests.post', side_effect=send_to_sms_outbox)
    def test_nexa_sms_client(self, mock_get_request, mock_get_settings):
        NOTIFIER = {
            "SMS": {
                "GATEWAYS": {
                    "NEXA": {
                        "CLIENT": "magic_notifier.sms_clients.nexa_client.NexaSmsClient",
                        "EMAIL": "sub_account",
                        "PASSWORD": "sub_account_password",
                        "SENDERID": "senderid"
                    }
                },
                "DEFAULT_GATEWAY": "NEXA"
            }
        }

        with self.settings(NOTIFIER=NOTIFIER):
            user = User.objects.create(email="testuser@localhost", username="testuser")
            not_profile = NotifyProfile.objects.create(phone_number="+237600000000",
                                                       user=user)

            subject = "Test magic notifier"
            notify(["sms"], subject, [user], final_message="Nice if you get this")

            self.assertGreater(len(sms_outbox), 0)  # type: ignore
            first_message = sms_outbox[0]  # type: ignore
            self.assertEqual(first_message.number, not_profile.phone_number)
            self.assertEqual(first_message.message, "Nice if you get this")


class PushNotificationTestCase(TestCase):

    def test_load_json(self):
        ctx = {
            'text': 'yes',
            'actions': [
                {
                    'text': 'wow',
                    'url': 'accept',
                    'method': 'post'
                },
                {
                    'text': 'meow',
                    'url': 'deny',
                    'method': 'get'
                }
            ],
            'data': {
                'love': 'you',
                'hate': 'no-one'
            }
        }
        push_content = render_to_string(f"notifier/base/push.json", ctx)
        print(push_content)
        self.assertIsInstance(json.loads(push_content), dict)

    def test_notification_builder_class(self):
        notif = NotificationBuilder("just a test").text("This is just a test").type('test', 'test_sub')\
            .link("http://lol").save()
        self.assertIsInstance(notif, Notification)
        seria = NotificationSerializer(instance=notif)
        print(notif)
        print(seria.data)

    def test_send_push_via_fcm(self):
        user = User.objects.create_user('testuser')
        notify(['push'], "Super cool", [user], template="testfcm", remove_notification_fields=['action', 'link',
                                                    'is_visible', 'is_encrypted'])


class LivePushNotificationTestCase(LiveServerTestCase):
    port = 8001

    def test_pusher_class(self):
        user = User.objects.create_user('testuser')
        NotifyProfile.objects.create(user=user)
        pusher = Pusher("just a test", [user], 'base', {'data': {'love': 'you', 'hate': 'no-one'},
                                                        'actions': [{'text':'accept', 'method':'post', 'url': 'http://'}]})
        notif = pusher.send()
        self.assertIsInstance(notif, Notification)
        seria = NotificationSerializer(instance=notif)
        print(notif)
        print(seria.data)


class WhatsappNotificationTestCase(LiveServerTestCase):

    def test_waha_client(self):
        WahaClient.send("+237693138363", "Bonjour Jeff")

    def test_whatsapper(self):
        user = User.objects.create(email="testuser@localhost", username="testuser",
                                   first_name="Jeff", last_name="Matt")
        not_profile = NotifyProfile.objects.create(phone_number="+237693138363",
                                                   user=user)
        whatsapper = Whatsapper([user], {},
                                final_message="Bonjour Jeff Matt. Votre code est XXXX")
        whatsapper.send()


class TelegramNotificationTestCase(LiveServerTestCase):

    def test_telethon_client(self):
        TelethonClient.send("+237693138363", "Jeff", "Matt",
                            "Bonjour Jeff. Voici ton code XXXX.", "default")

    def test_telegramer(self):
        user = User.objects.create(email="testuser@localhost", username="testuser",
                                   first_name="Jeff", last_name="Matt")
        not_profile = NotifyProfile.objects.create(phone_number="+237693138363",
                                                   user=user)
        telegramer = Telegramer([user], {},
                                final_message="Bonjour Jeff Matt")
        telegramer.send()


class AllNotificationTestCase(LiveServerTestCase):

    def test_01_send_to_sms_whatsapp_telegram(self):
        user = User.objects.create(email="testuser@localhost", username="testuser",
                                   first_name="Jeff", last_name="Matt")
        not_profile = NotifyProfile.objects.create(phone_number="+237698948836",
                                                   user=user)
        notify(['sms', 'whatsapp', 'telegram'], "Code",[user],
               final_message="Salut Fedim Stephane. Ceci est un test d'envoi de code")
