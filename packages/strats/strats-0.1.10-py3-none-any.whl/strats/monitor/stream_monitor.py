import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional

from strats.core import Clock, Monitor, State

logger = logging.getLogger(__name__)


class StreamClient(ABC):
    @abstractmethod
    async def stream(self):
        pass


class StreamMonitor(Monitor):
    def __init__(
        self,
        client: StreamClient,
        **kwargs,
    ):
        self.client = client
        self.client_name = client.__class__.__name__

        super().__init__(**kwargs)

    async def run(self, clock: Clock, state: Optional[State]):
        await self.delay()
        self.set_descriptor(state)
        logger.info(f"{self.name} start")

        success = self.exec_on_init()
        if not success:
            return

        try:
            async for source in self.client.stream():
                self.exec_on_pre_event(source)
                self.update_data_descriptor(state, source)
                self.exec_on_post_event(source)

        except asyncio.CancelledError:
            # To avoid "ERROR:asyncio:Task exception was never retrieved",
            # Re-raise the CancelledError
            raise
        except Exception as e:
            # Unexpected error
            logger.error(
                f"Stream error in {self.name}, but maybe in the `stream` function"
                f" in {self.client_name}: {e}"
            )
        finally:
            self.exec_on_delete()
            logger.info(f"{self.name} stopped")
