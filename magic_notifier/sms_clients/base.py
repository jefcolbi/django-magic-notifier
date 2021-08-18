"""
"""


class BaseSmsClient:

    @classmethod
    def send(cls, number: str, text: str):
        raise NotImplementedError

if __name__ == "__main__":
    CGSmsClient.send("0000000000", "Cava ma tigresse")
