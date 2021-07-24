import importlib
import logging
import traceback

from django.contrib.auth import get_user_model

from magic_notifier.models import Notification

logger = logging.getLogger('notifier')

User = get_user_model()


class NotificationBuilder:
    def __init__(self, text):
        self.__text = text
        self.__user = None
        self.__type = None
        self.__sub_type = None
        self.__mode = None
        self.__actions = []
        self.__link = None
        self.__data = {}
        self.__image = None

    def text(self, text=None):
        if text is None:
            return self.__text

        if not isinstance(text, str):
            raise ValueError("text should be a string")

        self.__text = text
        return self

    def link(self, link=None):
        if link is None:
            return self.__link

        if not isinstance(link, str):
            raise ValueError("link should be a string")

        self.__link = link
        return self

    def mode(self, mode=None):
        if mode is None:
            return self.__mode

        if not isinstance(mode, str):
            raise ValueError("mode should be a string")

        self.__mode = mode
        return self

    def type(self, type: str = None, sub_stype: str = None):
        if type is None:
            return self.__type, self.__sub_type

        self.__type = type
        self.__sub_type = sub_stype
        return self

    def action(self, text=None, method: str = None, url: str = None, fields: dict = {}):
        if method is None or url is None or text is None:
            return self.__actions

        action = {"method": method, "url": url, "fields": fields, "text": text}
        self.__actions.append(action)
        return self

    def actions(self, actions: list = None):
        if actions is None:
            return self.__actions

        if not isinstance(actions, list):
            raise ValueError("actions should be a list")

        self.__actions.extend(actions)
        return self

    def user(self, user: User = None):
        if not user:
            return self.__user

        if isinstance(user, User):
            self.__user = user
        else:
            raise ValueError("Sender should be User or Reach instance")

        return self

    def data(self, data: dict = None):
        if data is None:
            return self.__data

        if isinstance(data, dict):
            self.__data.update(data)
            return self

        raise ValueError("data should be a dict")

    def image(self, image=None):
        if image is None:
            return self.__image

        self.__image = image
        return self

    def save(self):
        notif = Notification.objects.create(
            text=self.__text,
            link=self.__link,
            user=self.__user,
            data=self.__data,
            actions=self.__actions,
            image=self.__image,
            type=self.__type,
            sub_type=self.__sub_type,
        )
        return notif

    def show(self):
        return (
            f"(text={self.__text}, link={self.__link}, user={self.__user}, "
            f"type={self.__type}, sub_stype={self.__sub_type}, mode={self.__mode},"
            f"data={self.__data}, actions={self.__actions}, image={self.__image}"
        )


def import_class(class_path:str):
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    assert hasattr(module, class_name), "class {} is not in {}".format(class_name, module_name)
    logger.debug('reading class {} from module {}'.format(class_name, module_name))
    cls = getattr(module, class_name)
    return cls