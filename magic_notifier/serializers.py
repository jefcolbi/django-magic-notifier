from rest_framework.serializers import ModelSerializer

from magic_notifier.models import Notification


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "text",
            "type",
            "sub_type",
            "link",
            "mode",
            "image",
            "actions",
            "data",
            "read",
            "sent",
        )
