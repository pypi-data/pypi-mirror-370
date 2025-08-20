import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Clock:
    def __init__(
        self,
        *,
        tz: Optional[ZoneInfo] = None,
        start_at: Optional[str] = None,
        speed: float = 1.0,
    ):
        self.tz = tz
        self.speed = speed
        self.is_mock = start_at is not None

        if self.is_mock:
            t = datetime.strptime(str(start_at), DATETIME_FORMAT)
            if tz:
                t = t.replace(tzinfo=tz)
            self.mock_datetime = t

    @property
    def datetime(self):
        if self.is_mock:
            return self.mock_datetime

        if self.tz:
            return datetime.now(self.tz)
        else:
            return datetime.now()

    @property
    def ohlc_datetime(self):
        return self.datetime.replace(second=0, microsecond=0)

    async def run(self):
        if not self.is_mock:
            return

        logger.info("mock clock start")
        try:
            while True:
                await asyncio.sleep(1 / self.speed)
                self.mock_datetime += timedelta(seconds=1)
        except asyncio.CancelledError:
            pass
        finally:
            logger.info("mock clock stopped")
