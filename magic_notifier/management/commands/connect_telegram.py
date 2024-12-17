from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from magic_notifier.telegram_clients.telethon import TelethonClient

User = get_user_model()


class Command(BaseCommand):
    """The command `test_email_template` is used to test a template email.
    This is very useful in development."""

    def add_arguments(self, parser):
        parser.add_argument('gateway', type=str, help="The gateway to connect")

    def handle(self, *args, **options):

        try:
            gateway = options['gateway']
            TelethonClient.get_client(gateway)
            print('Done!')
        except Exception:
            import traceback
            traceback.print_exc()
