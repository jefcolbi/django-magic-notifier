import logging

import requests

logger = logging.getLogger("notifier")


class CGSmsClient:
    sub_account = ""
    sub_account_pass = ""

    def __init__(self, number, text):
        pass

    @classmethod
    def send(cls, number: str, text: str):
        params = {
            "sub_account": cls.sub_account,
            "sub_account_pass": cls.sub_account_pass,
            "action": "send_sms",
            "message": text,
            "recipients": number,
        }
        res = requests.get("http://cheapglobalsms.com/api_v1", params=params)
        # print(res.content)
        # print(res.json())


if __name__ == "__main__":
    CGSmsClient.send("0000000000", "Cava ma tigresse")
