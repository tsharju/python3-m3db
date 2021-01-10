from datetime import datetime, timezone
from unittest import mock

import httpx
import pytest
import snappy

from m3db.client import M3DBClient
from m3db.prompb.remote_pb2 import WriteRequest


@pytest.mark.parametrize("ts", [None, 0])
@mock.patch("m3db.utils.get_utc_timestamp_ms", return_value=1607925092393)
def test_client_write(mock_timestamp, ts, httpx_mock):
    client = M3DBClient(host="localhost", port=7205)

    httpx_mock.add_response(method="POST", url="https://localhost:7205/api/v1/prom/remote/write")

    client.write("test", 100.0, labels={"label": "value"}, timestamp=ts)
    client.flush()

    request = httpx_mock.get_request()
    
    data = request.read()
    write_request = WriteRequest()
    write_request.ParseFromString(snappy.uncompress(data))

    assert write_request.timeseries[0].labels[0].name == "__name__"
    assert write_request.timeseries[0].labels[0].value == "test"
    assert write_request.timeseries[0].labels[1].name == "label"
    assert write_request.timeseries[0].labels[1].value == "value"
    assert write_request.timeseries[0].samples[0].value == 100.0
    if ts is not None:
        mock_timestamp.assert_not_called()
        assert write_request.timeseries[0].samples[0].timestamp == 0
    else:
        mock_timestamp.assert_called_once()
        assert write_request.timeseries[0].samples[0].timestamp == 1607925092393
