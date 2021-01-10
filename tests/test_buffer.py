from unittest import mock

from m3db.buffer import TimeSeriesBuffer


@mock.patch("m3db.utils.get_utc_timestamp_ms", side_effect=[0, 1, 2])
def test_write_series(mock_timestamp):
    series_buffer = TimeSeriesBuffer()
    
    series_buffer.write("local_test", 0.1)
    assert "local_test{}" in series_buffer._timeseries_buffer.keys()
    timeseries = series_buffer._timeseries_buffer["local_test{}"]
    assert len(timeseries.labels) == 1 # always has the __name__ label
    assert len(timeseries.samples) == 1
    assert timeseries.samples[0].value == 0.1

@mock.patch("m3db.utils.get_utc_timestamp_ms", side_effect=[0, 1, 2])
def test_write_series_with_labels(mock_timestamp):
    series_buffer = TimeSeriesBuffer()
    
    series_buffer.write("local_test", 0.1, labels={"host": "localhost"})
    assert "local_test{host=localhost}" in series_buffer._timeseries_buffer.keys()
    timeseries = series_buffer._timeseries_buffer["local_test{host=localhost}"]
    assert len(timeseries.labels) == 2
    assert timeseries.labels[0].name == "__name__"
    assert timeseries.labels[0].value == "local_test"
    assert timeseries.labels[1].name == "host"
    assert timeseries.labels[1].value == "localhost"
    assert len(timeseries.samples) == 1
    assert timeseries.samples[0].value == 0.1

    series_buffer.write("local_test", 0.2, labels={"env": "test"})
    timeseries = series_buffer._timeseries_buffer["local_test{env=test}"]
    assert len(timeseries.labels) == 2
    assert len(timeseries.samples) == 1
    assert timeseries.samples[0].value == 0.2

    series_buffer.write("local_test", 0.3, labels={"env": "test"})
    timeseries = series_buffer._timeseries_buffer["local_test{env=test}"]
    assert len(timeseries.labels) == 2
    assert len(timeseries.samples) == 2
    assert timeseries.samples[0].value == 0.2
    assert timeseries.samples[1].value == 0.3

    write_request = series_buffer.flush()
    assert len(series_buffer._timeseries_buffer) == 0
    assert len(write_request.timeseries) == 2

    assert series_buffer.flush() is None
