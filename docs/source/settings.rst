Settings
---------

Django Magic Notifier works mainly with settings. Many objects used by DMN are configurable

GENERAL SETTINGS
===================

All the next settings goes in a dictionary named NOTIFIER, for example::

    NOTIFIER = {
        'THREADED': True
    }

Enable, disable email notifications, Default True (Enabled)::

    'EMAIL_ACTIVE': True

Enable, disable sms notifications, Default False (Disabled)::

    'SMS_ACTIVE': False

Enable, disable push notifications, Default False (Disabled)::

    'PUSH_ACTIVE': False

Threading, sending or not notifications in background. Default False::

    'THREADED': False

NOTIFIER EMAIL SETTINGS
===========================

The next settings goes in a dictionary named EMAIL in NOTIFIER, like this::

    NOTIFIER = {
        'EMAIL': {
        }
    }

Specify the default EMAIL gateway::

    'DEFAULT_GATEWAY': 'default'

Speficifing an email gateway is by adding a dictionary in the EMAIL dicitionary::

    'default': {
        "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient"
        "HOST": "",
        "PORT": 0,
        "USER": "",
        "FROM": "",
        "PASSWORD": "",
        "USE_SSL": False,
        "USE_TLS": False,
    }

Full example::

    NOTIFIER = {
        'EMAIL': {
            'DEFAULT_GATEWAY': 'smtp_1',
            'smtp_1': {
                "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient"
                "HOST": "",
                "PORT": 0,
                "USER": "",
                "FROM": "",
                "PASSWORD": "",
                "USE_SSL": False,
                "USE_TLS": False,
            },
            'smtp_2': {
                "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient"
                "HOST": "",
                "PORT": 0,
                "USER": "",
                "FROM": "",
                "PASSWORD": "",
                "USE_SSL": False,
                "USE_TLS": False,
            },
            'custom': {
                "CLIENT": "app.email_clients.CustomEmailClient"
                "Option1": "",
                "Option2": 0,
                "Option3": "",
            }
        }
    }

NOTIFIER SMS SETTINGS
======================

The next settings goes in a dictionary named SMS in NOTIFIER, like this::

    NOTIFIER = {
        'SMS': {

        }
    }

Specify the default EMAIL gateway::

    'DEFAULT_GATEWAY': 'default'

Speficifing a sms gateway is by adding a dictionary in the SMS dictionary::

    'default': {
        "CLIENT": "magic_notifier.sms_clients.twilio_client.TwilioClient"
        "ACCOUNT": "",
        "TOKEN": 0,
        "FROM_NUMBER": "",
    }

Full example::

    NOTIFIER = {
        'SMS': {
            'DEFAULT_GATEWAY': 'twilio',
            'twilio': {
                "CLIENT": "magic_notifier.sms_clients.twilio_client.TwilioClient"
                "ACCOUNT": "",
                "TOKEN": 0,
                "FROM_NUMBER": "",
            },
            'custom': {
                "CLIENT": "app.sms_clients.CustomEmailClient"
                "Option1": "",
                "Option2": 0,
                "Option3": "",
            }
        }
    }

DMN needs a way to get a phone number from a User object. GET USER NUMBER must be path a function that accepts
one parameter of type User. Default **`'magic_notifer.utils.get_user_number'`**::

    'GET_USER_NUMBER': 'path.to.function'

NOTIFIER PUSH SETTINGS
======================

To connect to push notification websocket, a client must have a token.
You need to specify a path to a function that returns a token given a
User instance. The signature of the function must be::

    def get_token_from_user(user) -> str:


Setting example::

    NOTIFIER = {
        "USER_FROM_WS_TOKEN_FUNCTION": 'magic_notifier.utils.get_user_from_ws_token'
    }
