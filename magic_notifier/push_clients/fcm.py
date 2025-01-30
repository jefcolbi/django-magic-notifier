from pyfcm import FCMNotification
from django.contrib.auth import get_user_model
from magic_notifier.models import Notification
from magic_notifier.utils import import_attribute

User = get_user_model()


class FCMClient:

    def send(self, user: User, notification: Notification, options: dict, remove_notification_fields=None):
        remove_notification_fields = [] if not remove_notification_fields else remove_notification_fields
        fcm_user_tokens = import_attribute(options['GET_TOKENS_FUNCTION'])

        fcm = FCMNotification(service_account_file=options["SERVICE_ACCOUNT_FILE"],
                              project_id=options['PROJECT_ID'])

        data = notification.to_dict()
        for field in remove_notification_fields:
            data.pop(field, None)

        for fcm_user_token in fcm_user_tokens:
            fcm.notify(fcm_token=fcm_user_token, notification_title=notification.subject,
                   data_payload=data)

