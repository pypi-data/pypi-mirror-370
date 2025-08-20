from __future__ import annotations

from typing import Any, Dict, Optional
import time
import random

import httpx

from flumes.logger import emit
from flumes.exceptions import AuthenticationError, NotFoundError, RateLimitError, TransportError
from flumes.exceptions import FlumesError

# ---------------------------------------------------------------------------
# Response handling helper
# ---------------------------------------------------------------------------

def _handle_response(resp: httpx.Response) -> dict:  # noqa: D401
    if resp.status_code < 300:
        return resp.json()
    rid = resp.headers.get("X-Request-Id")
    rl_remaining = None
    try:
        rl_remaining = int(resp.headers.get("X-RateLimit-Remaining", ""))
    except ValueError:
        pass
    retry_after = None
    try:
        retry_after = int(resp.headers.get("Retry-After", ""))
    except ValueError:
        pass
    msg = (resp.json().get("message") if resp.headers.get("content-type","" ).startswith("application/json") else resp.text) or ""
    if resp.status_code == 401:
        raise AuthenticationError(msg or "Unauthorized", code="AUTH_INVALID_API_KEY", status=401, request_id=rid)
    if resp.status_code == 403:
        raise FlumesError(msg or "Forbidden", code="NOT_AUTHORIZED", status=403, request_id=rid)
    if resp.status_code == 404:
        raise NotFoundError(msg or "Not found", code="ENTITY_NOT_FOUND", status=404, request_id=rid)
    if resp.status_code == 409:
        raise FlumesError(msg or "Conflict", code="CONFLICT", status=409, request_id=rid)
    if resp.status_code == 422:
        raise FlumesError(msg or "Validation failed", code="VALIDATION_FAILED", status=422, request_id=rid)
    if resp.status_code == 429:
        raise RateLimitError(msg or "Rate limited", code="RATE_LIMITED", status=429, request_id=rid, retry_after_sec=retry_after, rate_limit_remaining=rl_remaining)
    if 500 <= resp.status_code < 600:
        raise FlumesError(msg or "Server error", code="SERVER_DEGRADED", status=resp.status_code, request_id=rid)
    raise TransportError(f"{resp.status_code}: {msg}", code="NETWORK", status=resp.status_code, request_id=rid)


# ---------------------------------------------------------------------------
# Abstract transport class
# ---------------------------------------------------------------------------

class BaseTransport:
    """Abstract transport providing CRUD helpers."""

    # legacy CRUD signatures kept for compatibility in older code paths
    def add(self, payload: dict) -> dict:  # noqa: D401
        raise NotImplementedError

    def get(self, memory_id: str) -> dict:  # noqa: D401
        raise NotImplementedError

    def search(self, params: dict) -> dict:  # noqa: D401
        raise NotImplementedError

    def delete(self, memory_id: str) -> dict:  # noqa: D401
        raise NotImplementedError

    def update(self, memory_id: str, payload: dict) -> dict:  # noqa: D401
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Remote HTTP transport
# ---------------------------------------------------------------------------

class RemoteTransport(BaseTransport):
    def __init__(self, base_url: str, api_key: str, timeout: int = 10, *, agent_id: Optional[str] = None, client: Optional[httpx.Client] = None):
        default_headers = {"Authorization": f"Bearer {api_key}", "Accept-Encoding": "gzip, deflate"}
        if agent_id:
            default_headers["X-Flumes-Agent"] = agent_id

        self.client = client or httpx.Client(
            base_url=base_url,
            headers=default_headers,
            timeout=httpx.Timeout(connect=2.0, read=25.0, write=10.0, pool=5.0) if isinstance(timeout, int) else timeout,
        )

    # ------------------------ CRUD ------------------------
    def add(self, payload: dict) -> dict:  # noqa: D401
        emit("memory.add.request", **payload)
        resp = self.client.post("/v1/memories/", json=payload)
        data = _handle_response(resp)
        emit("memory.stored", **data)
        return data

    def get(self, memory_id: str) -> dict:  # noqa: D401
        resp = self.client.get(f"/v1/memories/{memory_id}")
        return _handle_response(resp)

    def search(self, params: dict) -> dict:  # noqa: D401
        resp = self.client.get("/v1/memories/", params=params)
        return _handle_response(resp)

    def delete(self, memory_id: str) -> dict:  # noqa: D401
        resp = self.client.delete(f"/v1/memories/{memory_id}")
        return _handle_response(resp)

    def update(self, memory_id: str, payload: dict) -> dict:  # noqa: D401
        resp = self.client.patch(f"/v1/memories/{memory_id}", json=payload)
        return _handle_response(resp)

    # --------------- New endpoints (v0) -----------------
    def context_assemble(self, body: dict, *, headers: Optional[Dict[str, str]] = None) -> dict:
        # Write-friendly retry only if Idempotency-Key present
        attempts = 2 if headers and headers.get("Idempotency-Key") else 1
        last_err = None
        for i in range(attempts):
            try:
                resp = self.client.post("/v0/context/assemble", json=body, headers=headers)
                return _handle_response(resp)
            except FlumesError as e:
                last_err = e
                if e.code in ("RATE_LIMITED", "SERVER_DEGRADED") and i + 1 < attempts:
                    sleep = (2 ** i) + random.random()
                    time.sleep(sleep)
                    continue
                raise
        if last_err:
            raise last_err
        raise TransportError("Unknown error", code="NETWORK", status=0)

    def recall(self, body: dict, *, headers: Optional[Dict[str, str]] = None) -> dict:
        # Idempotent; retry on network/5xx
        for i in range(3):
            try:
                resp = self.client.post("/v0/recall", json=body, headers=headers)
                return _handle_response(resp)
            except FlumesError as e:
                if e.code in ("SERVER_DEGRADED",):
                    time.sleep((2 ** i) + random.random())
                    continue
                raise

    def memories_list(self, params: dict, *, headers: Optional[Dict[str, str]] = None) -> dict:
        for i in range(3):
            try:
                resp = self.client.get("/v0/memories", params=params, headers=headers)
                return _handle_response(resp)
            except FlumesError as e:
                if e.code in ("SERVER_DEGRADED",):
                    time.sleep((2 ** i) + random.random())
                    continue
                raise

    def health(self) -> dict:
        resp = self.client.get("/v0/health")
        return _handle_response(resp)

    def meta(self) -> dict:
        resp = self.client.get("/v0/meta")
        return _handle_response(resp)


# ---- LocalTransport has been removed from the public SDK to avoid
# heavy backend dependencies.  Kept here as a private stub so imports
# in legacy code fail clearly.


class LocalTransport(BaseTransport):
    def __init__(self):  # noqa: D401
        raise FlumesError(
            "Local transport is not available in the public SDK. "
            "Clone the Flumes monorepo and run from source if you need in-process mode."
        )

    # Dummy implementations (never reached)
    def add(self, payload: dict) -> dict:  # noqa: D401
        raise NotImplementedError

    def get(self, memory_id: str) -> dict:  # noqa: D401
        raise NotImplementedError

    def search(self, params: dict) -> dict:  # noqa: D401
        raise NotImplementedError

    def delete(self, memory_id: str) -> dict:  # noqa: D401
        raise NotImplementedError

    def update(self, memory_id: str, payload: dict) -> dict:  # noqa: D401
        raise NotImplementedError
