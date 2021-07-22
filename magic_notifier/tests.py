from django.test import TestCase
from django.contrib.auth import  get_user_model
from magic_notifier.notifier import notify
from django.test.utils import override_settings
from django.core import mail

User = get_user_model()


#@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class EmailTestCase(TestCase):
    """Class to test emails sending"""

    def test_simple_direct_email(self):
        user = User(email="jefcolbi@gmail.com", username="jefcolbi")

        subject = "Test magic notifier"
        notify(["email"], subject, [user], final_message="Super si tu reçois ce mail Jef")

        self.assertGreater(len(mail.outbox), 0)
        first_message = mail.outbox[0]
        self.assertEqual(first_message.to, [user.email])
        self.assertEqual(first_message.subject, subject)
