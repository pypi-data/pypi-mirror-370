import asyncio
import logging
import threading
from dataclasses import dataclass, field
from typing import Optional

from prometheus_client import REGISTRY, CollectorRegistry

from .clock import Clock
from .monitor import Monitor
from .state import State
from .strategy import Strategy

logger = logging.getLogger(__name__)


@dataclass
class StratsConfig:
    install_access_log: bool = False
    drop_access_log_paths: tuple[str, ...] = field(default_factory=tuple)


class Kernel:
    def __init__(
        self,
        *,
        config: Optional[StratsConfig] = None,
        state: Optional[State] = None,
        strategy: Optional[Strategy] = None,
        monitors: Optional[list[Monitor]] = None,
        clock: Clock = Clock(),
        registry: Optional[CollectorRegistry] = None,
    ):
        self.config = config or StratsConfig()
        self.state = state
        self.state_stop_event = None

        # There is no event loop yet, so don't create an `asyncio.Event`.
        self.monitors = monitors
        self.monitor_tasks: dict[str, asyncio.Task] = {}
        self.monitor_started_ats: dict[str, asyncio.Task] = {}

        self.strategy = strategy
        self.strategy_task = None
        self.strategy_started_at = None

        self.clock = clock
        self.clock_task = None

        self.registry = registry or REGISTRY

    async def start_strategy(self):
        if self.strategy is None:
            raise ValueError("Missing strategy configuration")

        if self.state is not None:
            self.state.set_queues()

        if self.strategy_task and not self.strategy_task.done():
            return

        # Since only Strategy reads from the queue, the queue is prepared in start_strategy.
        if self.state is not None:
            self.state.flush_queue()

        self.strategy_task = asyncio.create_task(
            _handle_error(self.strategy.run)(self.clock, self.state),
            name="strategy",
        )
        self.strategy_started_at = self.clock.datetime

    async def stop_strategy(self, timeout=5.0):
        if self.strategy is None:
            raise ValueError("Missing strategy configuration")
        if self.strategy_task.done():
            raise ValueError("Strategy is already stopped")

        if "__str__" in type(self.strategy).__dict__:
            logger.info("stop strategy")
            logger.info(f"strategy details: {self.strategy}")

        self.strategy_started_at = None
        self.strategy_task.cancel()
        try:
            await self.strategy_task
        except asyncio.CancelledError:
            pass

    async def start_monitors(self):
        if self.monitors is None:
            raise ValueError("Missing monitors configuration")

        if self.state is not None:
            self.state.set_queues()

            self.state_stop_event = threading.Event()
            self.state.run(self.state_stop_event)

        for monitor in self.monitors:
            task = self.monitor_tasks.get(monitor.name)
            if task and not task.done():
                continue

            self.monitor_tasks[monitor.name] = asyncio.create_task(
                _handle_error(monitor.run)(self.clock, self.state),
                name=monitor.name,
            )
            self.monitor_started_ats[monitor.name] = self.clock.datetime

    async def stop_monitors(self, timeout=5.0):
        if self.monitors is None:
            raise ValueError("Missing monitors configuration")

        self.monitor_started_ats = {}

        for task in self.monitor_tasks.values():
            if not task.done():
                # we should await canceled task complete
                # cf. https://docs.python.org/ja/3.13/library/asyncio-task.html#asyncio.Task.cancel
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self.state is not None:
            self.state_stop_event.set()
            self.state.sync_to_async_queue_thread.join()

    async def start_clock(self):
        if not self.clock.is_mock:
            raise ValueError("Clock is not mock")

        if self.clock_task and not self.clock_task.done():
            return

        self.clock_task = asyncio.create_task(
            _handle_error(self.clock.run)(),
            name="clock",
        )

    async def stop_clock(self, timeout=5.0):
        if not self.clock.is_mock:
            raise ValueError("Clock is not mock")
        if self.clock_task.done():
            raise ValueError("Clock is already stopped")

        self.clock_task.cancel()
        try:
            await self.clock_task
        except asyncio.CancelledError:
            pass


def _handle_error(func):
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except asyncio.CancelledError:
            logger.info("handle cancel process")
            raise
        except Exception as e:
            logger.error(f"got unexpected exception: {e}")

    return wrapper
