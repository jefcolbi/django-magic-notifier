import asyncio

from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from django.conf import settings
import time


class TelethonClient:

    running_clients = {}

    @classmethod
    def get_client(cls, gateway:str, **kwargs) -> TelegramClient:
        if gateway in cls.running_clients:
            return cls.running_clients[gateway]

        api_id = kwargs["API_ID"]
        api_hash = kwargs["API_HASH"]

        client = TelegramClient(gateway, api_id, api_hash)
        client.start()
        cls.running_clients[gateway] = client
        return client
    @classmethod
    def send(cls, number:str, first_name:str, last_name:str, text:str,
             gateway:str, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if 'There is no current event loop' in str(e):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise

        client = cls.get_client(gateway, **kwargs)
        client.loop.run_until_complete(cls.async_send(client, number, first_name,
                        last_name, text))


    @classmethod
    async def async_send(cls, client, number:str, first_name:str, last_name:str, text:str):
        contact = InputPhoneContact(client_id=0, phone=number,
                                    first_name=first_name, last_name=last_name)
        result = await client(ImportContactsRequest([contact]))
        print(result)
        result = await client.send_message(number, text)
        print(result)
