from django.conf import settings

AVAILABLE_MODES = [("user", "User"), ("admin", "Admin")]
NOTIFIER_SETTINGS = getattr(settings, "NOTIFIER", {})

EMAIL_ACTIVE = NOTIFIER_SETTINGS.get('EMAIL_ACTIVE', True)
SMS_ACTIVE = NOTIFIER_SETTINGS.get('SMS_ACTIVE', False)
PUSH_ACTIVE = NOTIFIER_SETTINGS.get('PUSH_ACTIVE', False)

NOTIFIER_AVAILABLE_MODES = NOTIFIER_SETTINGS.get('DEFAULT_MODES', AVAILABLE_MODES)
NOTIFIER_DEFAULT_MODE = NOTIFIER_SETTINGS.get("DEFAULT_MODE", "user")

NOTIFIER_THREADED = NOTIFIER_SETTINGS.get('THREADED', False)

NOTIFIER_EMAIL = NOTIFIER_SETTINGS.get('EMAIL', {})
NOTIFIER_EMAIL_DEFAULT_GATEWAY = NOTIFIER_EMAIL.get('DEFAULT_GATEWAY', 'default')

if NOTIFIER_EMAIL_DEFAULT_GATEWAY == "default":
    if "default" not in NOTIFIER_EMAIL:
        # we build the default dict from django standard smtp settings
        assert settings.EMAIL_HOST, "You have not defined any DEFAULT EMAIL settings and no django email settings detected."
        NOTIFIER_EMAIL["default"] = {
            "HOST": settings.EMAIL_HOST,
            "PORT": settings.EMAIL_PORT,
            "USER": settings.EMAIL_HOST_USER,
            "FROM": settings.DEFAULT_FROM_EMAIL,
            "PASSWORD": settings.EMAIL_HOST_PASSWORD,
            "USE_SSL": getattr(settings, "EMAIL_USE_SSL", False),
            "USE_TLS": getattr(settings, "EMAIL_USE_TLS", False),
            "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient"
        }

