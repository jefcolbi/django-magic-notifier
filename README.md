# Django Magic Notifier

[![travis django-magic-notifier](https://api.travis-ci.com/jefcolbi/django-magic-notifier.svg?branch=main)](https://travis-ci.com/github/jefcolbi/django-magic-notifier) [![coverage django-magic-notifier](https://coveralls.io/repos/github/jefcolbi/django-magic-notifier/badge.svg?branch=main)](https://coveralls.io/github/jefcolbi/django-magic-notifier?branch=main) [![Pypi current version](https://img.shields.io/pypi/v/django-magic-notifier.svg)](https://pypi.org/project/django-magic-notifier/) [![Documentation](http://readthedocs.org/projects/django-magic-notifier/badge/?version=stable)](https://django-magic-notifier.readthedocs.io/en/stable/) ![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)
![Python versions](https://img.shields.io/pypi/pyversions/django-magic-notifier) ![Django versions](https://img.shields.io/pypi/djversions/django-magic-notifier)  
![](https://img.shields.io/github/stars/jefcolbi/django-magic-notifier.svg) ![](https://img.shields.io/github/forks/jefcolbi/django-magic-notifier.svg) ![](https://img.shields.io/github/tag/jefcolbi/django-magic-notifier.svg) ![](https://img.shields.io/github/issues/jefcolbi/django-magic-notifier.svg)

### Why Django Magic Notifier  
Sending notifications in Django has always been a complex subject. Django Magic Notifier solves this by providing only one function **notify()**. The library [will] support sending notifications via email, sms and push notifications.  

### Documentation
[Full documentation](https://django-magic-notifier.readthedocs.io/en/latest/)

### Features

- Send emails
- Send sms, TWILIO support
- Send push notifications
- Support templates
- Simple API
- Support files
- Support multiple gateways
- Extensible
- Support MJML


### Installation
> pip install --upgrade django-magic-notifier

### Usage
##### 1. Configure settings
If you have already configured SMTP EMAIL SETTINGS in django settings then can ignore this step. Else add a NOTIFIER dict in your settings like this

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
            "PASSWORD": "********",
            "CLIENT": "magic_notifier.email_clients.django_email.DjangoEmailClient",
        }
    },
    "USER_FROM_WS_TOKEN_FUNCTION": 'magic_notifier.utils.get_user_from_ws_token'
}
```

##### 2. Create templates
Create a folder named **notifier** in one of app's templates dir. In this folder create another folder named **my_template** 
then create your base templates in this folder. Example:  

*app_name/templates/notifier/my_template/email.html*
```
{% extends "base_notifier/email.html" %}
{% block content %}
<tr>
    <td><p>Hello {{ user.email }}
    </td>
</tr>
{% endblock %}
```  

*app_name/templates/notifier/my_template/email.txt*
```
{% extends "base_notifier/email.txt" %}
{% block content %}
Hello {{ user.email }}
{% endblock %}
```  

As you can see, the user to whom the notification goes is automatically added 
in the template's context. To avoid any clash don't send the key `'user'` 
in the context of the  **notifiy()** function presented below.

Note that it is DMN (Django Magic Notifier) that has the base_notifier template.

##### 3. Send notifications
To send a notification via email do
```python
    from magic_notifier.notifier import notify

    # send an email from direct string
    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, [user], final_message="Nice if you get this")

    # send an email from a template
    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, [user], template='hello')
    
    # send a sms from a template
    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["sms"], subject, [user], template='hello')
    
    # send a notification via email and sms from a template
    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email", "sms"], subject, [user], template='hello')
```

### Docs and support
https://django-magic-notifier.readthedocs.io/en/latest/index.html


### Roadmap

- Generate full documentation
- Translate documentation


### Contributing
Contribution are welcome.

### License
As per the license, feel free to use the library as you want.
