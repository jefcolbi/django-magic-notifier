Installation
------------

You can install **Django Magic Notifier** via various ways

PIP::

    > pip install django-magic-notifier

Git::

    > git clone https://github.com/jefcolbi/django-magic-notifier
    > cd django-magic-notifier
    > python setup.py install


If you intend to use Push notifications, then you need to include DMN
consumers in your django channels routing

Python::

    application = ProtocolTypeRouter({
        # Django's ASGI application to handle traditional HTTP requests
        "http": django_asgi_app,

        # WebSocket chat handler
        "websocket": URLRouter([
                    path("ws/notifications/<str:token>/", PushNotifConsumer.as_asgi()),
                ])
        }
    )
