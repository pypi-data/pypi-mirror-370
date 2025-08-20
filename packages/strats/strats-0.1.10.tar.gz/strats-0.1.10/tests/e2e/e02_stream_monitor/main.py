import asyncio
from collections.abc import AsyncGenerator

from strats import Strats
from strats.monitor import StreamClient, StreamMonitor


class SampleStreamClient(StreamClient):
    async def stream(self) -> AsyncGenerator[int]:
        for i in range(10):
            await asyncio.sleep(1)
            yield i


def create_app():
    stream_monitor = StreamMonitor(client=SampleStreamClient())
    return Strats(monitors=[stream_monitor]).create_app()
