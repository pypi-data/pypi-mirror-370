from collections.abc import AsyncGenerator

from strats import Strats
from strats.monitor import StreamClient, StreamMonitor


class SampleStreamClient(StreamClient):
    async def stream(self) -> AsyncGenerator[int]:
        raise ValueError("ERROR IN STREAM_CLIENT")
        yield 1


def create_app():
    return Strats(
        monitors=[
            StreamMonitor(
                client=SampleStreamClient(),
            )
        ],
    ).create_app()
