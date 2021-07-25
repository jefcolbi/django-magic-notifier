from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from magic_notifier.notifier import notify

User = get_user_model()


class EmailTestCase(TestCase):
    """Class to test emails sending"""

    def test_simple_direct_email(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], final_message="Nice if you get this")

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)

    def test_template_html_txt_email(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='base')

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
        self.assertEqual(len(first_message.alternatives), 1)

    def test_template_txt_email(self):
        user = User(email="testuser@localhost", username="testuser")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], template='hello')

        self.assertGreater(len(mail.outbox), 0) # type: ignore
        first_message = mail.outbox[0] # type: ignore
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
        self.assertEqual(len(first_message.alternatives), 0)
