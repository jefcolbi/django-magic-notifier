********
Ninagram
********
A framework built on top Django and python-telegram-bot!


Why Ninagram?
-------------

If you ever developed a Telegram bot using python-telegram-bot rapidly you will need to have persitence, you will discover that you write again and again the same code with a slightly difference and you start dealing with conversation-oriented bots.
It is true that python-telegram-bot has his own system to solve those problems like ConversationHandler and the new persistence system introduced in the v12.
But it was not sufficient for me so i decided to extend it. Ninagram use the Django ORM to provide persistence and a simple but yet powerful system based on the **State-step pattern** to handle conversational bots.
But Ninagram always comes with plenty of features like a SessionMiddleware, a runtime permisions system and States from Models.

.. image:: https://img.shields.io/pypi/l/ninagram
.. image:: https://img.shields.io/pypi/v/ninagram

Installation
------------

``$pip install --upgrade ninagram``

Features
--------
    - Persistence with Django ORM
    - Simple and power States (machine)
    - SessionMiddleware
    - Automatic usage of default Django User model
    - Django 2.2 supported. Plug-and-play.
    - Fine grained permissions (States and Steps)
    - States generation from Models
    - Runtime storage

Usage
-----
.. code-block:: python

    django-admin startproject testbot
    cd testbot
    python manage.py startapp base
    python manage.py startbot base
    python manage.py runbot

Docs and support
----------------
You can find the documentation at https://ninagram.readthedocs.org
For any question join https://t.me/

Roadmap
-------
    - Using JSON to declare the States of a bot
    - Simple language to declare Actions and match them to PTB methods (Bot API functions)
    - Studio, to build bot with drag-and-drop.

Contributing
------------
Contribution are welcome and required. The only rule is to **not break the State-Step pattern**.

License
-------
As per the license, feel free to use the the framework as you want.