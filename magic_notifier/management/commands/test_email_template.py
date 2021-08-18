from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from magic_notifier.notifier import notify

User = get_user_model()


class Command(BaseCommand):
    """The command `test_email_template` is used to test a template email.
    This is very useful in development."""

    def add_arguments(self, parser):
        parser.add_argument('template', type=str, help="The template to test")
        parser.add_argument('email', type=str, help="The email to use")
        parser.add_argument('-s', '--subject', type=str, default='Testing email template', required=False,
                            help="The subject of email. default to `Testing email template`")
        parser.add_argument('-a', '--account', type=str, default='default', required=False,
                            help="The smtp account. default to `default`")

    def handle(self, *args, **options):

        try:
            template = options['template']
            subject = options['subject']
            account = options['account']
            user_email = options['email']

            print(f"Sending email from template {template} to {user_email}")


            user = User(email=user_email, username=user_email)
            notify(["email"], subject=subject, smtp_account=account, receivers=[user], template=template,
                   context={})

            print('Done!')
        except Exception:
            import traceback
            traceback.print_exc()
