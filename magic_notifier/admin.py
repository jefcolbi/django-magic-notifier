from django.contrib import admin

from magic_notifier.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass
