from m3db import utils

def test_get_utc_timestamp_ms():
    now = utils.get_utc_timestamp_ms()
    assert len(str(now)) >= 13
