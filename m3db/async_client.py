from typing import Mapping, Optional

import anyio

from .client_base import M3DBClientBase


class AsyncM3DBClient(M3DBClientBase):
    async def write(
        self,
        name: str,
        sample: float,
        *,
        labels: Optional[Mapping] = None,
        timestamp: Optional[int] = None,
    ):
        pass
