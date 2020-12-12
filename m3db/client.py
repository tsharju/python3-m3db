import logging
from enum import Enum
from typing import Mapping, Optional

import httpx
import snappy

from .client_base import M3DBClientBase

logger = logging.getLogger(__name__)


class M3DBClient(M3DBClientBase):
    def write(
        self,
        name: str,
        sample: float,
        *,
        labels: Optional[Mapping] = None,
        timestamp: Optional[int] = None,
    ):
        self.buffer.write(name, sample, labels=labels, timestamp=timestamp)

    def flush(self):
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

        try:
            r = httpx.post(url, content=body, headers=headers, auth=auth)
            if 200 <= r.status_code < 300:
                pass
        except Exception as e:
            logger.error("Write failed")
            raise e
