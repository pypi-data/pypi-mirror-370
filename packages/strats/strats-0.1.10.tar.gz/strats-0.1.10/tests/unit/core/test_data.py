from dataclasses import dataclass
from unittest.mock import ANY, Mock, call

from strats.core import Data, State


@dataclass
class DummySource:
    s: int = 0


@dataclass
class DummyData:
    d: str = "0"


class DummyMetrics:
    def __init__(self, m=0.0):
        self.m: float = m


def test_data_update():
    def dummy_source_to_data(source: DummySource, _current_data: DummyData) -> DummyData:
        return DummyData(d=str(source.s))

    def dummy_data_to_metrics(data: DummyData, metrics: DummyMetrics):
        metrics.m = float(data.d)

    class DummyState(State):
        num = Data(
            data=DummyData(),
            metrics=DummyMetrics(),
            source_to_data=dummy_source_to_data,
            data_to_metrics=dummy_data_to_metrics,
        )

    state = DummyState()

    assert state.num.d == "0"
    assert DummyState.num._metrics.m == 0.0

    state.num = DummySource(s=1)
    assert state.num.d == "1"
    assert DummyState.num._metrics.m == 1.0

    del state.num
    assert state.num.d == "0"
    # assert DummyState.num._metrics.m == 0.0  # FIXME: the metrics is not reset


def test_data_lifecycle_hook():
    # Mock Parent
    lifecycle = Mock()

    # Mock children
    on_init = lifecycle.on_init
    on_delete = lifecycle.on_delete
    on_pre_event = lifecycle.on_pre_event
    on_post_event = lifecycle.on_post_event

    source_to_data = lifecycle.source_to_data
    source_to_data.side_effect = lambda s, _: DummyData(d=str(s.s))

    data_to_metrics = lifecycle.data_to_metrics

    class DummyState(State):
        num = Data(
            data=DummyData(),
            metrics=DummyMetrics(),
            source_to_data=source_to_data,
            data_to_metrics=data_to_metrics,
            on_init=on_init,
            on_delete=on_delete,
            on_pre_event=on_pre_event,
            on_post_event=on_post_event,
        )

    state = DummyState()

    # Update state data
    source = DummySource(s=123)
    state.num = source

    # Delete state data
    del state.num

    # Test the calls order
    assert lifecycle.mock_calls == [
        call.on_init(),
        call.on_pre_event(state, source),
        call.source_to_data(source, ANY),
        call.data_to_metrics(DummyData(d="123"), ANY),
        call.on_post_event(state, DummyData(d="123")),
        call.on_delete(state),
    ]
