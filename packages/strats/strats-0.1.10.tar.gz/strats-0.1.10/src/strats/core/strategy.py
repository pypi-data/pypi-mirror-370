from abc import ABC, abstractmethod

from .clock import Clock
from .state import State


class Strategy(ABC):
    @abstractmethod
    async def run(self, clock: Clock, state: State):
        pass
