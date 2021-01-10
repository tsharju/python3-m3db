import platform
from typing import Optional

from .buffer import TimeSeriesBuffer
from .version import version


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
