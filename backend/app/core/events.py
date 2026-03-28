import asyncio
import json


class EventBroadcaster:
    def __init__(self) -> None:
        self._listeners: set[asyncio.Queue[str]] = set()

    async def subscribe(self):
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._listeners.add(queue)
        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            self._listeners.discard(queue)

    async def publish(self, event: str, data: dict) -> None:
        payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        for listener in list(self._listeners):
            await listener.put(payload)


broadcaster = EventBroadcaster()
