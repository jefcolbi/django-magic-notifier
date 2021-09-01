from django.conf import settings

from tests.example.settings import NOTIFIER

AVAILABLE_MODES = [("user", "User"), ("admin", "Admin")]
NOTIFIER_SETTINGS = getattr(settings, "NOTIFIER", {})

SMTP_ACTIVE = NOTIFIER_SETTINGS.get('SMTP_ACTIVE', True)
SMS_ACTIVE = NOTIFIER_SETTINGS.get('SMS_ACTIVE', False)
PUSH_ACTIVE = NOTIFIER_SETTINGS.get('PUSH_ACTIVE', False)

NOTIFIER_AVAILABLE_MODES = NOTIFIER_SETTINGS.get('DEFAULT_MODES', AVAILABLE_MODES)
NOTIFIER_DEFAULT_MODE = NOTIFIER_SETTINGS.get("DEFAULT_MODE", "user")

NOTIFIER_THREADED = NOTIFIER_SETTINGS.get('THREADED', False)

if SMTP_ACTIVE:
    NOTIFIER_SMTP = NOTIFIER_SETTINGS.get('SMTP', {})

    if "default" not in NOTIFIER_SMTP:
        # we build the default dict from django standard smtp settings
        assert settings.EMAIL_HOST, "You have not defined any DEFAULT SMTP settings and no django smtp settings detected."
        NOTIFIER_SMTP["default"] = {
            "HOST": settings.EMAIL_HOST,
            "PORT": settings.EMAIL_PORT,
            "USER": settings.EMAIL_HOST_USER,
            "FROM": settings.DEFAULT_FROM_EMAIL,
            "PASSWORD": settings.EMAIL_HOST_PASSWORD,
            "USE_SSL": getattr(settings, "EMAIL_USE_SSL", False),
            "USE_TLS": getattr(settings, "EMAIL_USE_TLS", False),
            "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient"
        }

NOTIFIER_SMS = NOTIFIER_SETTINGS.get('SMS', {})
NOTIFIER_SMS_DEFAULT_GATEWAY = NOTIFIER_SETTINGS.get('DEFAULT_GATEWAY', 'default')
NOTIFIER_SMS_GATEWAYS = NOTIFIER_SETTINGS.get('GATEWAYS', {})
