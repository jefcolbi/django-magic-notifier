********
Django Magic Notifier
********
A notifications library for Djangonauts

.. image:: https://travis-ci.org/django-magic-notifier/django-magic-notifier.svg?branch=master
    :target: https://travis-ci.org/django-magic-notifier/django-magic-notifier
    :alt: Build status on Travis-CI

.. image:: https://coveralls.io/repos/github/django-magic-notifier/django-magic-notifier/badge.svg?branch=master
    :target: https://coveralls.io/github/django-magic-notifier/django-magic-notifier?branch=master

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


Why Django Magic Notifier?
-------------

Sending notifications in Django has always been a complex subject. Django Magic Notifier solves this by
providing only one function `notify()`

Installation
------------

``$pip install --upgrade django-magic-notifier``

Features
--------
    - Send emails
    - Sens sms
    - Send push messages
    - Support custom EmailClient
    - Support custom SmsClient

Usage
-----
.. code-block:: python

    django-admin startproject testbot
    cd testbot
    python manage.py startapp base

Docs and support
----------------
You can find the documentation at https://django-magic-notifier.readthedocs.org

Roadmap
-------
    - Write all tests
    - Generate full documentation
    - Translate documentation

Contributing
------------
Contribution are welcome and required.

License
-------
As per the license, feel free to use the the framework as you want.
