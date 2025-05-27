import json
from operator import mod

from django import VERSION as DJANGO_VERSION
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.utils.translation import gettext as _

if DJANGO_VERSION[0] >= 3 and DJANGO_VERSION[1] >= 1:
    from django.db.models import JSONField
else:
    class JSONField(models.TextField):
        """Simple JSON field that stores python structures as JSON strings
        on database.
        """

        def from_db_value(self, value, *args, **kwargs):
            return self.to_python(value)

        def to_python(self, value):
            """
            Convert the input JSON value into python structures, raises
            django.core.exceptions.ValidationError if the data can't be converted.
            """
            if self.blank and not value:
                return None
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception as e:
                    raise ValidationError(str(e))
            else:
                return value

        def validate(self, value, model_instance):
            """Check value is a valid JSON string, raise ValidationError on
            error."""
            if isinstance(value, str):
                super(JSONField, self).validate(value, model_instance)
                try:
                    json.loads(value)
                except Exception as e:
                    raise ValidationError(str(e))

        def get_prep_value(self, value):
            """Convert value to JSON string before save"""
            try:
                return json.dumps(value)
            except Exception as e:
                raise ValidationError(str(e))

        def value_from_object(self, obj):
            """Return value dumped to string."""
            val = super(JSONField, self).value_from_object(obj)
            return self.get_prep_value(val)

from .settings import NOTIFIER_AVAILABLE_MODES, NOTIFIER_DEFAULT_MODE

User = get_user_model()


class Notification(models.Model):

    id = models.BigAutoField(primary_key=True)
    user: models.ForeignKey = models.ForeignKey(
        User, models.CASCADE, null=True, blank=True, related_name="magic_notifications"
    )
    inited_by: models.ForeignKey = models.ForeignKey(
        User, models.CASCADE, null=True, blank=True, related_name="magic_notifications_inited"
    )
    subject: models.CharField = models.CharField(max_length=255, null=True, blank=True)
    text: models.TextField = models.TextField()
    type: models.CharField = models.CharField(max_length=30)
    sub_type: models.CharField = models.CharField(max_length=30, null=True, blank=True)
    link: models.CharField = models.CharField(_("The link associated"), max_length=255)
    image: models.ImageField = models.ImageField(upload_to="notifications", null=True, blank=True)
    is_visible: models.BooleanField = models.BooleanField(default=True)
    is_encrypted: models.BooleanField = models.BooleanField(default=False)
    actions: JSONField = JSONField(default=dict)
    data: JSONField = JSONField(default=dict)
    read: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    sent: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    expires: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    mode: models.CharField = models.CharField(
        max_length=10, default=NOTIFIER_DEFAULT_MODE, choices=NOTIFIER_AVAILABLE_MODES
    )
    masked: models.BooleanField = models.BooleanField(default=False)

    def __str__(self):
        if self.user and self.user.username:
            user_name = self.user.username
        else:
            user_name = ""
        return "{} Notif #{}".format(user_name, self.id)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def mark_read(self):
        from django.utils import timezone
        self.read = timezone.now()
        self.save()

    def to_dict(self):
        return {'type': self.type, 'sub_type': self.sub_type,
                'link': self.link, 'is_visible': self.is_visible,
                'is_encrypted': self.is_encrypted, 'action': self.actions,
                'data': self.data}


class NotifyProfile(models.Model):

    id = models.BigAutoField(primary_key=True)
    phone_number: models.CharField = models.CharField(max_length=20, null=True, blank=True)
    current_channel: models.CharField = models.CharField(max_length=255, null=True, blank=True)
    user: models.OneToOneField = models.OneToOneField(User, models.CASCADE)
