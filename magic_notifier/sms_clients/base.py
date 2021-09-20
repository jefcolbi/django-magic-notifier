"""
"""


class BaseSmsClient:

    @classmethod
    def send(cls, number: str, text: str, **kwargs):
        raise NotImplementedError
