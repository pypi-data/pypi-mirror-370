import asyncio
import logging
import weakref
from abc import ABC, abstractmethod
from typing import Callable, Optional

from .clock import Clock
from .state import State

logger = logging.getLogger(__name__)


class Monitor(ABC):
    """Base class for monitoring functionality"""

    _counter = 0
    _subclasses: weakref.WeakSet = weakref.WeakSet()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        cls._counter = 0  # each subclass starts from 0
        Monitor._subclasses.add(cls)

    @classmethod
    def reset_counters(cls):
        cls._counter = 0
        for sub in list(cls._subclasses):
            sub._counter = 0

    def __init__(
        self,
        name: Optional[str] = None,
        data_name: Optional[str] = None,
        start_delay_seconds: int = 0,
        # Lifecycle Hook
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_pre_event: Optional[Callable] = None,
        on_post_event: Optional[Callable] = None,
    ):
        # Update class-specific counter
        type(self)._counter += 1

        # Initialize common attributes
        self.name = name or f"{type(self).__name__}_{type(self)._counter}"
        self.data_name = data_name
        self.start_delay_seconds = start_delay_seconds

        # Set up lifecycle hooks
        self.on_init = on_init
        self.on_delete = on_delete
        self.on_pre_event = on_pre_event
        self.on_post_event = on_post_event

    @abstractmethod
    async def run(self, clock: Clock, state: Optional[State]):
        pass

    async def delay(self):
        if self.start_delay_seconds > 0:
            await asyncio.sleep(self.start_delay_seconds)

    def set_descriptor(self, state: Optional[State]):
        self.data_descriptor = None
        if state is not None and self.data_name:
            if self.data_name in type(state).__dict__:
                self.data_descriptor = type(state).__dict__[self.data_name]
            else:
                raise ValueError(f"data_name: `{self.data_name}` is not found in State")

    def exec_hook(self, f: Optional[Callable], f_name: str, *args) -> bool:
        if f is None:
            return True
        try:
            f(*args)
            return True
        except Exception as e:
            logger.error(f"lifecycle `{f_name}` error in {self.name}: {e}")
            return False

    def exec_on_init(self) -> bool:
        return self.exec_hook(self.on_init, "on_init")

    def exec_on_delete(self) -> bool:
        return self.exec_hook(self.on_delete, "on_delete")

    def exec_on_pre_event(self, source) -> bool:
        return self.exec_hook(self.on_pre_event, "on_pre_event", source)

    def exec_on_post_event(self, source) -> bool:
        return self.exec_hook(self.on_post_event, "on_post_event", source)

    def update_data_descriptor(self, state, source):
        if self.data_descriptor is None:
            return True
        try:
            self.data_descriptor.__set__(state, source)
            return True
        except Exception as e:
            logger.error(f"failed to update state.{self.data_name} in {self.name}: {e}")
            return False
