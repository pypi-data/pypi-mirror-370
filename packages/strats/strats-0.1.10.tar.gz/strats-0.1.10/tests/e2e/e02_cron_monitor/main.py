from zoneinfo import ZoneInfo

from strats import Clock, Strats
from strats.monitor import CronMonitor


async def cron_job(clock, state):
    print("job: ", clock.datetime)


def create_app():
    return Strats(
        clock=Clock(
            start_at="2025-01-01 12:04:50",
            tz=ZoneInfo("Asia/Tokyo"),
        ),
        monitors=[
            CronMonitor(
                cron_job=cron_job,
                cron_schedule="* * * * *",  # every minutes
            )
        ],
    ).create_app()
