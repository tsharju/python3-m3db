import logging
from enum import Enum

import httpx

from .client_base import M3DBClientBase

logger = logging.getLogger(__name__)


class M3DBClient(M3DBClientBase):
    def flush(self):
        request = self._serialize_request()

        if request is None:
            return

        with httpx.Client() as client:
            try:
                r = client.post(
                    request.url,
                    content=request.payload,
                    headers=request.headers,
                    auth=request.auth,
                )
                if 200 <= r.status_code < 300:
                    pass
            except Exception as e:
                logger.error("Write failed")
                raise e
