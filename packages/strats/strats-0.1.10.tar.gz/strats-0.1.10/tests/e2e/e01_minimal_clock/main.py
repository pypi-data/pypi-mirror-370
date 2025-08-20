from zoneinfo import ZoneInfo

from strats import Clock, Strats


def create_app():
    return Strats(
        clock=Clock(
            start_at="2025-01-01 12:00:00",
            tz=ZoneInfo("Asia/Tokyo"),
            speed=2,
        ),
    ).create_app()
