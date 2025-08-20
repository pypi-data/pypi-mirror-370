from __future__ import annotations

import asyncio
from typing import List, Optional

from flumes.client import MemoryClient
from flumes.models import Message


class AsyncMemoryClient:
    """Async wrapper around the synchronous ``MemoryClient`` (MVP)."""

    def __init__(self, **kwargs):
        self._inner = MemoryClient(**kwargs)
        # In future we will replace _inner with an async transport.

    # --------------------------------------------------
    async def add(self, messages: List[Message], **kwargs):
        return await asyncio.to_thread(self._inner.add, messages, **kwargs)

    async def get(self, memory_id: str):
        return await asyncio.to_thread(self._inner.get, memory_id)

    async def search(self, **kwargs):
        return await asyncio.to_thread(self._inner.search, **kwargs)

    async def delete(self, memory_id: str):
        return await asyncio.to_thread(self._inner.delete, memory_id)

    async def update(self, memory_id: str, *, memory: str, metadata: Optional[dict] = None):
        return await asyncio.to_thread(self._inner.update, memory_id, memory=memory, metadata=metadata)

    # --------------------------------------------------
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # nothing to clean up yet
        return False
