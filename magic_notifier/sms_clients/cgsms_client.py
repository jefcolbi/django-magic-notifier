import requests
import logging
from notifier.

logger = logging.getLogger("notif")


class CGSmsClient:
    sub_account = "jefcolbi@gmail.com"
    sub_account_pass = "cheapglobalsms01$"

    def __init__(self, number, text):
        pass

    @classmethod
    def send(cls, number: str, text: str):
        logger.info(f"Sending SMS {text} TO {number}")
        if not number.startswith("+237"):
            number = f"+237{number}"
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
    CGSmsClient.send("693480847", "Cava ma tigresse")
