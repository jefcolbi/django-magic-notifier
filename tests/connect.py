import asyncio
import websockets
import json

async def hello():
    async with websockets.connect("ws://localhost:8000/ws/notifications/72dcdc3dd3a292d1846ad30f88befcb6b7691edd/") as websocket:
        data = await websocket.recv()
        print(data)
        notif = json.loads(data)
        await websocket.send(json.dumps({'type':'markread', 'notification': notif['id']}))
        await websocket.recv()

        all_notifs = await websocket.send(json.dumps({'type': 'unread'}))
        print(await websocket.recv())

asyncio.run(hello())