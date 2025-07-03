from django.contrib import admin

from magic_notifier.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'type', 'sub_type')
