import platform
from dataclasses import dataclass
from typing import Mapping, Optional, Tuple

import snappy

from .buffer import TimeSeriesBuffer
from .version import version


@dataclass
class WriteRequest:
    url: str
    headers: Mapping[str, str]
    payload: str
    auth: Optional[Tuple[str, str]]


class M3DBClientBase:

    USER_AGENT_STRING = f"python3-m3db/{version} Python/{platform.python_version()}"

    buffer: TimeSeriesBuffer

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.buffer = TimeSeriesBuffer()

    def write(
        self,
        name: str,
        sample: float,
        *,
        labels: Optional[Mapping] = None,
        timestamp: Optional[int] = None,
    ):
        self.buffer.write(name, sample, labels=labels, timestamp=timestamp)

    def _serialize_request(self) -> Optional[WriteRequest]:
        request = self.buffer.flush()

        if request is None:  # nothing to flush
            return

        body = snappy.compress(request.SerializeToString())

        if self.use_tls:
            scheme = "https"
        else:
            scheme = "http"

        url = f"{scheme}://{self.host}:{self.port}/api/v1/prom/remote/write"
        headers = {
            "content-encoding": "snappy",
            "content-type": "application/x-protobuf",
            "x-prometheus-remote-write-version": "0.1.0",
            "user-agent": M3DBClientBase.USER_AGENT_STRING,
        }

        auth = None
        if self.username is not None and self.password is not None:
            auth = (self.username, self.password)

        return WriteRequest(url, headers, body, auth)
