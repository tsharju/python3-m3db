from typing import Dict, Mapping, Optional
from urllib.parse import urlencode

from attr import dataclass
from llist import dllist, dllistnode  # type: ignore

from . import utils
from .prompb.remote_pb2 import WriteRequest
from .prompb.types_pb2 import TimeSeries

Labels = Dict[str, str]


def _labels_string(labels) -> str:
    return urlencode(labels)


def _labels_string_from_timeseries(timeseries: TimeSeries) -> str:
    return ""


class TimeSeriesBuffer:

    _timeseries_buffer: Dict[str, TimeSeries]
    _ordered_keys: dllist
    _key_to_node: Dict[str, dllistnode]

    def __init__(self, maxsize: Optional[int] = None):
        self._timeseries_buffer = {}
        self._ordered_keys = dllist()
        self._key_to_node = {}

    def write(
        self,
        name: str,
        sample: float,
        labels: Optional[Mapping] = None,
        timestamp: Optional[int] = None,
    ):
        if labels is None:
            labels = {}
        if timestamp is None:
            timestamp = utils.get_utc_timestamp_ms()

        labels_string = _labels_string(labels=labels)
        timeseries_key = f"{name}{{{labels_string}}}"

        timeseries = self._timeseries_buffer.get(timeseries_key)

        if timeseries is None:  # initialize new timeseries
            timeseries = TimeSeries()
            label = timeseries.labels.add()
            label.name = "__name__"
            label.value = name
            if labels is not None:
                for k, v in labels.items():
                    l = timeseries.labels.add()
                    l.name = k
                    l.value = v
            self._timeseries_buffer[timeseries_key] = timeseries
            node = self._ordered_keys.append(timeseries_key)
            self._key_to_node[timeseries_key] = node
        else:  # update the order
            node = self._key_to_node[timeseries_key]
            self._ordered_keys.remove(node)
            self._ordered_keys.append(node)

        # add new sample
        s = timeseries.samples.add()
        s.value = sample
        s.timestamp = timestamp

    def flush(self, max_series: Optional[int] = None) -> Optional[WriteRequest]:
        if max_series is None:
            max_series = len(self._timeseries_buffer)
        write_request = WriteRequest()
        for i in range(max_series):
            try:
                timeseries_key = self._ordered_keys.popleft()
                self._key_to_node.pop(timeseries_key)
                timeseries = self._timeseries_buffer.pop(timeseries_key)
                write_request.timeseries.append(timeseries)
            except ValueError as e:
                # No more timeseries left in the buffer
                break
        if len(write_request.timeseries) > 0:
            return write_request
        else:
            return None
