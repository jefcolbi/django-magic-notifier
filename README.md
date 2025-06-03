# Django Magic Notifier

[![Travis CI](https://api.travis-ci.com/jefcolbi/django-magic-notifier.svg?branch=main)](https://travis-ci.com/github/jefcolbi/django-magic-notifier) [![Coverage](https://coveralls.io/repos/github/jefcolbi/django-magic-notifier/badge.svg?branch=main)](https://coveralls.io/github/jefcolbi/django-magic-notifier?branch=main) [![PyPI Version](https://img.shields.io/pypi/v/django-magic-notifier.svg)](https://pypi.org/project/django-magic-notifier/) [![Documentation](http://readthedocs.org/projects/django-magic-notifier/badge/?version=stable)](https://django-magic-notifier.readthedocs.io/en/stable/) ![Python Versions](https://img.shields.io/pypi/pyversions/django-magic-notifier) ![Django Versions](https://img.shields.io/pypi/djversions/django-magic-notifier)

[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/django-magic-notifier/)

---

### Why Choose Django Magic Notifier?

Managing notifications in Django applications can often be a complex and cumbersome task. **Django Magic Notifier (DMN)** simplifies this by consolidating all your notification needs into a single, powerful API: `notify()`. Whether you need to send emails, SMS, WhatsApp messages, Telegram notifications, or push notifications, DMN handles it all seamlessly.

---

## Features

- **Unified Notification API**: One function `notify()` to handle all notification types.
- **Multi-Channel Support**: Email, SMS, WhatsApp, Telegram, and push notifications.
- **Gateway Flexibility**: Configure multiple gateways per channel with ease.
- **Template-Based Messages**: Use templates for consistent and professional notifications.
- **File Attachments**: Include files in your notifications.
- **Asynchronous Notifications**: Threaded support for background processing.
- **Extensibility**: Add custom gateways or notification types.
- **MJML Support**: Use modern, responsive email designs.

---

## Installation

Install Django Magic Notifier using pip:

```bash
pip install --upgrade django-magic-notifier
```

---

## Configuration

Add the `NOTIFIER` configuration to your Django `settings.py` file. Below is an example of a complete configuration:

```python
NOTIFIER = {
    "EMAIL": {
        "default": {
            "HOST": "localhost",
            "PORT": 587,
            "USE_TLS": True,
            "USE_SSL": False,
            "USER": "root@localhost",
            "FROM": "Root <root@localhost>",
            "PASSWORD": "password",
            "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient",
        },
        "ses": {
            "CLIENT": "magic_notifier.email_clients.amazon_ses.AmazonSesClient",
            "AWS_ACCESS_KEY": "****************",
            "AWS_SECRET_KEY": "****************************************",
            "AWS_REGION_NAME": "eu-north-1",
            "AWS_REGION_ENDPOINT": "https://email.eu-north-1.amazonaws.com",
            "FROM": "Service <account@service.se>",
        },
        "DEFAULT_GATEWAY": "ses",  # use amazon ses as the default gateway
        "FALLBACKS": ["default"]  # if the default gateway fails, fallback to these gateways
    },
    "WHATSAPP": {
        "DEFAULT_GATEWAY": "waha",
        "GATEWAYS": {
            "waha": {
                "BASE_URL": "http://localhost:3000"
            }
        }
    },
    "TELEGRAM": {
        "DEFAULT_GATEWAY": "default",
        "GATEWAYS": {
            "default": {
                "API_ID": "xxxxxx",
                "API_HASH": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            }
        }
    },
    "SMS": {
        "DEFAULT_GATEWAY": "TWILIO",
        "GATEWAYS": {
            "TWILIO": {
                "CLIENT": "magic_notifier.sms_clients.twilio_client.TwilioClient",
                "ACCOUNT": "account_sid",
                "TOKEN": "auth_token",
                "FROM_NUMBER": "+1234567890"
            }
        }
    },
    "USER_FROM_WS_TOKEN_FUNCTION": "magic_notifier.utils.get_user_from_ws_token",
    "GET_USER_NUMBER": "magic_notifier.utils.get_user_number",
    "THREADED": True
}
```

### Key Settings

- **EMAIL**: Configure your email gateway, including host, port, and credentials.
- **WHATSAPP**: Define the WhatsApp gateway with its base URL.
- **TELEGRAM**: Configure Telegram with API credentials.
- **SMS**: Specify SMS gateways such as Twilio, Nexa, or others.
- **THREADED**: Enable background processing for notifications.

---

## Usage

### Sending Notifications

The `notify()` function is your gateway to all notification types.

#### Basic Email Notification
```python
from magic_notifier.notifier import notify

user = User.objects.get(email="testuser@localhost")
subject = "Welcome!"
notify(["email"], subject, [user], final_message="Welcome to our platform!")
```

#### SMS Notification with Template
```python
notify(["sms"], "Account Alert", [user], template="account_alert")
```

#### Multi-Channel Notification
```python
notify(["email", "sms"], "System Update", [user], final_message="The system will be down for maintenance.")
```

#### WhatsApp Notification
```python
notify(["whatsapp"], "Welcome", [user], final_message="Hello! This is a WhatsApp test message.")
```

#### Telegram Notification
```python
notify(["telegram"], "Welcome", [user], final_message="Hello! This is a Telegram test message.")
```

### Passing Context to Templates
You can pass additional context to your templates via the `context` argument, note that the `user` 
object is automatically passed:

```python
context = {
    "discount": 20
}
notify(["email"], "Special Offer", [user], template="special_offer", context=context)
```

In the template:
```html
{% block content %}
<p>Hi {{ user.first_name }},</p>
<p>We are excited to offer you a {{ discount }}% discount on your next purchase!</p>
{% endblock %}
```

### Overriding Gateways
You can override default gateways directly when sending notifications:

#### Override Email Gateway
```python
notify(["email"], "Custom Email Gateway", [user], final_message="This uses a custom email gateway.", email_gateway="custom_gateway")
```

#### Override SMS Gateway
```python
notify(["sms"], "Custom SMS Gateway", [user], final_message="This uses a custom SMS gateway.", sms_gateway="custom_sms_gateway")
```

#### Override WhatsApp Gateway
```python
notify(["whatsapp"], "Custom WhatsApp Gateway", [user], final_message="This uses a custom WhatsApp gateway.", whatsapp_gateway="custom_whatsapp_gateway")
```

#### Override Telegram Gateway
```python
notify(["telegram"], "Custom Telegram Gateway", [user], final_message="This uses a custom Telegram gateway.", telegram_gateway="custom_telegram_gateway")
```

### Template Creation and Resolution
When using templates, Django Magic Notifier looks for specific files depending on the notification channels. The template value designates a folder, not a file. Files are checked in the following order for each channel:

- **Email**: `email.mjml` -> `email.html` -> `email.txt`
- **SMS**: `sms.txt`
- **WhatsApp**: `whatsapp.txt` -> `sms.txt`
- **Telegram**: `telegram.txt` -> `sms.txt`

If a file is not found, the next file in the sequence is checked. If no files are found, an error is raised.

#### Example
Suppose `notify()` is called as follows:
```python
notify(["telegram"], "Welcome", [user], template="welcome")
```

The following files will be checked in order:
1. `notifier/welcome/telegram.txt`
2. `notifier/welcome/sms.txt`

Ensure that at least one of these files exists in your templates directory.

---

## Advanced Features

### Sending Files
Attach files to your notifications:
```python
files = ["/path/to/file.pdf"]
notify(["email"], "Invoice", [user], final_message="Your invoice is attached.", files=files)
```

### Sending to Specific Receiver Groups
The `notify()` function supports predefined values for the `receivers` argument to target specific user groups:

#### Sending to Admin Users
```python
notify(["email"], "Admin Alert", "admins", final_message="This is a message for all admin users.")
```

#### Sending to Staff Users
```python
notify(["email"], "Staff Notification", "staff", final_message="This message is for all staff members.")
```

#### Sending to All Users
```python
notify(["email"], "Global Announcement", "all", final_message="This is a message for all users.")
```

#### Sending to Non-Staff Users
```python
notify(["email"], "Non-Staff Update", "all-staff", final_message="This message is for users who are not staff.")
```

#### Sending to Non-Admin Users
```python
notify(["email"], "User Alert", "all-admins", final_message="This is a message for all users except admins.")
```

### Asynchronous Processing
Enable threaded notifications for better performance:
```python
notify(["sms"], "Alert", [user], final_message="This is a test.", threaded=True)
```

---

## Testing

DMN includes comprehensive test cases for all features. To run tests:
```bash
python manage.py test
```

---

## Roadmap

- Extend support for additional messaging platforms.

---

## Contributing

We welcome contributions! To get started, fork the repository, make your changes, and submit a pull request. Refer to our [contributing guidelines](CONTRIBUTING.md) for more details.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Support

File an issue on [GitHub](https://github.com/jefcolbi/django-magic-notifier/issues).

