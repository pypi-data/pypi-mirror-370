from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class QueueMsg:
    source: Optional[Any] = None
    data: Optional[Any] = None
    dedup: bool = True


class Data:
    def __init__(
        self,
        *,
        data=None,
        metrics=None,
        source_to_data=None,
        data_to_metrics=None,
        on_init: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_pre_event: Optional[Callable] = None,
        on_post_event: Optional[Callable] = None,
        enqueue: bool = True,
        dedup: bool = True,
    ):
        # Data and Metrics
        self.initial_data = data
        self.initial_metrics = metrics
        self._data = data
        self._metrics = metrics

        # ETL
        self.source_to_data = source_to_data
        self.data_to_metrics = data_to_metrics

        # Lifecycle Hook
        self.on_init = on_init
        self.on_delete = on_delete
        self.on_pre_event = on_pre_event
        self.on_post_event = on_post_event

        # Queue settings
        self.enqueue = enqueue
        self.dedup = dedup

        # Descriptor instance name
        self._data_name = None

    def __set_name__(self, owner, name):
        self._data_name = name

        if self.on_init is not None:
            self.on_init()

    def __get__(self, instance, owner=None):
        # When accessed as a class attribute
        if instance is None:
            return self
        return self._data

    def __set__(self, instance, new_source):
        if self.on_pre_event is not None:
            self.on_pre_event(instance, new_source)

        # Source -> Data
        if self.source_to_data is not None:
            new_data = self.source_to_data(new_source, self._data)
        else:
            new_data = new_source

        # Update Data
        self._data = new_data

        if self.enqueue and hasattr(instance, "sync_queue"):
            instance.sync_queue.put(
                QueueMsg(
                    source=new_source,
                    data=new_data,
                    dedup=self.dedup,
                )
            )

        # Update Metrics if needed
        if self.data_to_metrics is not None:
            # Data -> Metrics
            self.data_to_metrics(new_data, self._metrics)

        if self.on_post_event is not None:
            self.on_post_event(instance, new_data)

    def __delete__(self, instance):
        if self.on_delete is not None:
            self.on_delete(instance)

        # Reset data and metrics
        self._data = self.initial_data
        self._metrics = self.initial_metrics  # FIXME: metrics is not reset
