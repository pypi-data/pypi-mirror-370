from __future__ import annotations

import asyncio
from typing import Optional

from autonomi_client import Client


class _AsyncClientManager:
    """Async client cache/manager per process.

    Lazily initializes one client for mainnet and one for alpha.
    Thread-safe via asyncio locks.
    """

    def __init__(self) -> None:
        self._mainnet_client: Optional[Client] = None
        self._alpha_client: Optional[Client] = None
        self._lock_mainnet = asyncio.Lock()
        self._lock_alpha = asyncio.Lock()

    async def get_client(self, *, alpha: bool) -> Client:
        if alpha:
            if self._alpha_client is None:
                async with self._lock_alpha:
                    if self._alpha_client is None:
                        self._alpha_client = await Client.init_alpha()
            return self._alpha_client
        else:
            if self._mainnet_client is None:
                async with self._lock_mainnet:
                    if self._mainnet_client is None:
                        self._mainnet_client = await Client.init()
            return self._mainnet_client

    async def close_all(self) -> None:
        # autonomi_client.Client might not expose close; if it does in future, implement it here
        self._mainnet_client = None
        self._alpha_client = None


async_client_manager = _AsyncClientManager()


