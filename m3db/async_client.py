import logging
from typing import Mapping, Optional

import anyio
import httpx

from .client_base import M3DBClientBase

logger = logging.getLogger(__name__)


class AsyncM3DBClient(M3DBClientBase):
    async def flush(self):
        request = self._serialize_request()

        if request is None:
            return

        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(
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
