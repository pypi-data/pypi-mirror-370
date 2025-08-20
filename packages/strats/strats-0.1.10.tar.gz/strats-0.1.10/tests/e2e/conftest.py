import pytest

from strats.core import Monitor


@pytest.fixture(autouse=True)
def _reset_monitor_counters():
    Monitor.reset_counters()
    yield
    Monitor.reset_counters()
