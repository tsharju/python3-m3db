from datetime import datetime, timezone


def get_utc_timestamp_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000.0)
