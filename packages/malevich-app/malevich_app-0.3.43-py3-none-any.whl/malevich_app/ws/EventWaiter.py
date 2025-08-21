import asyncio
from typing import Tuple, Optional
from malevich_app.export.abstract.abstract import WSMessage


class EventWaiter:
    def __init__(self):
        self.futures = {}

    def set_result(self, msg: WSMessage) -> bool:
        future_operation = self.futures.pop(msg.id, None)
        if future_operation is not None:
            future, operation = future_operation
            if operation != msg.operation:
                self.futures[msg.id] = future_operation
                raise Exception("wrong set_result operation")
            future.set_result((msg.payload, msg.error))
            return True
        return False

    async def wait(self, id: str, operation: str) -> Tuple[Optional[str], Optional[str]]:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[id] = (future, operation)
        return await future


waiter = EventWaiter()
