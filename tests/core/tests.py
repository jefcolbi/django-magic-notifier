import time
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from magic_notifier.notifier import notify

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
