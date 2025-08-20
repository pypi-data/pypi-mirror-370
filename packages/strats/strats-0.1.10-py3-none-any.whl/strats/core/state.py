import asyncio
import logging
import queue
import threading

from strats.internal.lru_set import LRUSet

logger = logging.getLogger(__name__)


class State:
    def __init__(self, dedup_cache_size=100):
        self.lruset = LRUSet(capacity=dedup_cache_size)

    def set_queues(self):
        """
        set_queues initializes both synchronous and asynchronous queues.

        To avoid attaching them to the default event loop,
        this function must be called after the FastAPI server has started.

        The State class has embedded queue and sync_queue. These serve as pipes
        connecting Data, State, and external components. The reason why State
        (rather than Kernel) holds these queues is that Data can only access State.
        """
        if not hasattr(self, "_initialized"):
            self.sync_queue = queue.Queue()
            self.queue = asyncio.Queue()
            self._initialized = True

    def flush_queue(self):
        self.queue = asyncio.Queue()

    def run(self, stop_event: threading.Event):
        loop = asyncio.get_running_loop()
        self.sync_to_async_queue_thread = threading.Thread(
            target=self._sync_to_async_queue,
            args=(loop, stop_event),
        )
        self.sync_to_async_queue_thread.start()

    def _sync_to_async_queue(
        self,
        loop: asyncio.AbstractEventLoop,
        stop_event: threading.Event,
    ):
        logger.info("sync_to_async_queue thread start")

        while not stop_event.is_set():
            try:
                item = self.sync_queue.get(timeout=1)
            except queue.Empty:
                continue

            if item is None:
                break  # the stop signal

            # dedup filter
            if item.dedup:
                if self.lruset.contains(item):
                    continue
                else:
                    self.lruset.add(item)

            # When scheduling callbacks from another thread,
            # `call_soon_threadsafe` must be used, since `call_soon` is not thread-safe.
            # cf. https://docs.python.org/ja/3.13/library/asyncio-eventloop.html#asyncio.loop.call_soon_threadsafe
            loop.call_soon_threadsafe(self.queue.put_nowait, item)

        logger.info("sync_to_async_queue thread stopped")
