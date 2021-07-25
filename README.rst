Django Magic Notifier
=====================

.. image:: https://api.travis-ci.com/jefcolbi/django-magic-notifier.svg?branch=main
    :target: https://travis-ci.com/github/jefcolbi/django-magic-notifier
    :alt: Build status on Travis-CI

.. image:: https://coveralls.io/repos/github/jefcolbi/django-magic-notifier/badge.svg?branch=main
    :target: https://coveralls.io/github/jefcolbi/django-magic-notifier?branch=main
    :alt: Coverage status on coverage.io

.. image:: https://img.shields.io/pypi/v/django-magic-notifier.svg
    :target: https://pypi.org/project/django-magic-notifier/
    :alt: Current version on PyPi

.. image:: http://readthedocs.org/projects/django-magic-notifier/badge/?version=stable
    :target: https://django-magic-notifier.readthedocs.io/en/stable/
    :alt: Documentation

.. image:: https://img.shields.io/pypi/pyversions/django-magic-notifier
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/djversions/django-magic-notifier
    :alt: PyPI - Django Version

.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat
    :alt: PR Welcomes


Why Django Magic Notifier?
--------------------------

Sending notifications in Django has always been a complex subject. Django Magic Notifier solves this by
providing only one function **notify()**. The library [will] support sending notifications via email, sms and push notifications.

Installation
--------------------------

``$pip install --upgrade django-magic-notifier``

Features
--------

- Send emails
- Email templates

Usage
-----

**1. Configure Settings**

If you have already configured SMTP SETTINGS via django settings then can ignore this step. Else add a NOTIFIER dict in your settings like this::

    NOTIFIER = {
        "SMTP": {
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
        }
        "THREADED": False,
    }

**2. Create email templates**

Create a folder named **notifier** in one of app's templates dir. In this folder create another folder named **base** then created your base templates in this folder. Example

*core/templates/notifier/base/email.html*::

    {% extends "base_notifier/email.html" %}

*core/templates/notifier/base/email.txt*::

    {% extends "base_notifier/email.txt" %}


*core/templates/notifier/hello/email.html*::

    {% extends "notifier/base/email.html" %}
    {% block content %}
    <tr>
        <td><p>Hello {{ user.email }}
        </td>
    </tr>
    {% endblock %}

*core/templates/notifier/hello/email.txt*::

    {% extends "notifier/hello/email.txt" %}
    {% block content %}
    >Hello {{ user.email }}
    {% endblock %}

As you can see, the user to whom the notification goes is automatically added in the template's context. To avoid any clash to don't use the key 'user' in the notifiy function presented below.

Note that it is DMN (Django Magic Notifier) that has the base_notifier template.

To send a notification via email do::

    from magic_notifier.notifier import notify

    # send an email from direct string
    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, [user], final_message="Nice if you get this")

    # send an email from a template
    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, [user], template='hello')


Docs and support
----------------

Coming


Roadmap
-------

- [] Send sms
- [] Send push notifications
- [] Generate full documentation
- [] Translate documentation


Contributing
-----------

Contribution are welcome.

License
-------

As per the license, feel free to use the library as you want.
