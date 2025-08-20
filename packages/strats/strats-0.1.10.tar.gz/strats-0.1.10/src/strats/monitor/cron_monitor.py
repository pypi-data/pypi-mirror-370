import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional

from croniter import croniter

from strats.core import Clock, Monitor, State

logger = logging.getLogger(__name__)


class CronMonitor(Monitor):
    def __init__(
        self,
        cron_job: Callable,
        cron_schedule: str,
        check_interval_sec: float = 0.5,
        **kwargs,
    ):
        self.cron_job = cron_job
        self.cron_schedule = cron_schedule
        self.check_interval_sec = check_interval_sec

        super().__init__(**kwargs)

    async def run(self, clock: Clock, state: Optional[State]):
        await self.delay()
        self.set_descriptor(state)
        logger.info(f"{self.name} start")

        success = self.exec_on_init()
        if not success:
            return

        schedule = croniter(self.cron_schedule, clock.datetime)
        try:
            next_time = schedule.get_next(datetime)
            while True:
                if clock.datetime >= next_time:
                    # Exec job
                    source = await self.cron_job(clock, state)

                    # Update state and lifecycle hooks
                    self.exec_on_pre_event(source)
                    self.update_data_descriptor(state, source)
                    self.exec_on_post_event(source)

                    # prepare next schedule
                    next_time = schedule.get_next(datetime)
                await asyncio.sleep(self.check_interval_sec)

        except asyncio.CancelledError:
            # To avoid "ERROR:asyncio:Task exception was never retrieved",
            # Re-raise the CancelledError
            raise
        except Exception as e:
            # Unexpected error
            logger.error(f"Error in {self.name}, but maybe in the `cron_job` function: {e}")
        finally:
            self.exec_on_delete()
            logger.info(f"{self.name} stopped")
