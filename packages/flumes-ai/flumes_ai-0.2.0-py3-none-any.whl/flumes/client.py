from __future__ import annotations

import os
from typing import List, Optional, Union, Dict, Any

from flumes.models import Message
from flumes.transport import RemoteTransport, LocalTransport, BaseTransport
from flumes.exceptions import FlumesError
from flumes.logger import emit
import hashlib
import time
from flumes.logger import emit


class MemoryClient:
    """Synchronous Memory client exposing simple and advanced APIs.

    Simple tier methods (entity-first, Mem0-like):
      - add(input, *, entity_id, namespace?, budget?, retrieval?, idempotency_key?)
      - search(query, *, entity_id, namespace?, top_k?, preset? | weights?, include_scores?, cursor?)
      - get_all(*, entity_id, namespace?, type?, tag?, archived?, before?, after?, sort?, limit?, cursor?)
      - for_entity(entity_id, namespace?, defaults?) -> bound client

    Advanced pass-throughs (thin mapping to REST):
      - context.assemble, recall.query, memories.list/update/delete, events.append, meta, health
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.flumes.ai",
        timeout: int = 120,
        agent_id: Optional[str] = None,
        namespace: str = "default",
        local: bool = False,
    ) -> None:
        if local:
            raise FlumesError("local=True is not supported in the public SDK distribution.")
        else:
            key = api_key or os.getenv("FLUMES_API_KEY")
            if not key:
                raise FlumesError("API key missing; set FLUMES_API_KEY or pass api_key=")
            self._transport = RemoteTransport(base_url, key, timeout=timeout, agent_id=agent_id)
        self._agent_id = agent_id
        self._namespace = namespace

    # ------------------------------------------------------------------
    # Simple tier
    # ------------------------------------------------------------------

    def for_entity(self, entity_id: str, *, namespace: Optional[str] = None, defaults: Optional[Dict[str, Any]] = None) -> "MemoryClient":
        """Return a derived client bound to an entity and optional namespace/defaults.

        Note: returns a lightweight wrapper that forwards calls with pre-filled args.
        """
        ns = namespace or self._namespace
        parent = self

        class _BoundClient:
            def add(self, input: Union[str, List[Message]], **kwargs):
                return parent.add(input, entity_id=entity_id, namespace=ns, **kwargs)

            def search(self, query: str, **kwargs):
                return parent.search(query, entity_id=entity_id, namespace=ns, **kwargs)

            def get_all(self, **kwargs):
                return parent.get_all(entity_id=entity_id, namespace=ns, **kwargs)

        return _BoundClient()  # type: ignore[return-value]

    def add(
        self,
        input: Union[str, List[Message]],
        *,
        entity_id: str,
        namespace: Optional[str] = None,
        budget: Optional[Union[str, Dict[str, Any]]] = None,
        retrieval: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        trace: Optional[bool] = None,
        include_snippet: bool = False,
        return_structured_facts: bool = False,
    ) -> dict:
        """Extract + store a turn via /v0/context/assemble with ingest enabled."""
        ns = namespace or self._namespace
        # Compose turn string if messages provided
        if isinstance(input, list):
            turn = "\n".join([f"{m.role}: {m.content}" if isinstance(m, Message) else f"{m['role']}: {m['content']}" for m in input])
        else:
            turn = input

        req: Dict[str, Any] = {
            "entity_id": entity_id,
            "namespace": ns,
            "turn": turn,
            "ingest": {"extract": True, "store_turn": "event", "upsert_conflicts": "smart"},
            "return": {"include": ["facts", "recent_events", "summary", "sources"]},
        }
        if include_snippet:
            req["seed_context"] = {"snippets": [turn]}
        if budget:
            if isinstance(budget, str):
                preset_map = {
                    "light": {"max_context_tokens": 400},
                    "standard": {"max_context_tokens": 1200},
                    "heavy": {"max_context_tokens": 2400},
                }
                req["budget"] = preset_map.get(budget, {"max_context_tokens": 1200})
            else:
                req["budget"] = budget
        if retrieval:
            req["retrieval"] = retrieval
        if trace is True:
            req["return"]["trace"] = True
        if return_structured_facts:
            req["return"]["include_structured_facts"] = True

        headers: Dict[str, str] = {}
        if self._agent_id:
            headers["X-Flumes-Agent"] = self._agent_id
        if idempotency_key == "":
            # explicit opt-out
            pass
        else:
            if not idempotency_key:
                # Derive a short-lived idempotency key for safe retries
                minute_bucket = int(time.time() // 60)
                h = hashlib.sha256(f"{entity_id}|{ns}|{minute_bucket}|{len(turn)}".encode()).hexdigest()[:32]
                idempotency_key = h
            headers["Idempotency-Key"] = idempotency_key

        emit("request", method="POST", url="/v0/context/assemble", headers={k: v for k, v in headers.items() if k != "Authorization"})
        resp = self._transport.context_assemble(req, headers=headers)
        emit("response", status=200, url="/v0/context/assemble", request_id=resp.get("request_id"))

        # Compute pack telemetry for callers
        token_counts = (resp.get("context") or {}).get("token_counts") or {}
        used = token_counts.get("planned")
        budget = (req.get("budget") or {})
        target = budget.get("max_context_tokens")
        hard_cap = {400: 600, 1200: 1500, 2400: 3000}.get(target, target)
        resp["pack"] = {"target_tokens": target, "hard_cap_tokens": hard_cap, "used_tokens": used, "dropped": (resp.get("context") or {}).get("budget_actions") or []}
        resp["idempotency_key"] = idempotency_key
        return resp

    # Legacy CRUD removed from public surface (use simple tier)

    def search(
        self,
        query: str,
        *,
        entity_id: Optional[str] = None,
        namespace: Optional[str] = None,
        top_k: Optional[int] = None,
        limit: Optional[int] = None,
        preset: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None,
        include_scores: Optional[bool] = None,
        cursor: Optional[str] = None,
        trace: Optional[bool] = None,
    ) -> dict:
        ns = namespace or self._namespace
        if preset and weights:
            raise FlumesError("VALIDATION_FAILED: provide either preset or weights, not both.")
        body: Dict[str, Any] = {
            "query": query,
            "entity_id": entity_id,
            "namespace": ns,
            "limit": limit or 16,
        }
        if preset:
            body["retrieval"] = {"preset": preset}
        if weights:
            body["retrieval"] = {"weights": weights}
        if top_k is not None:
            body.setdefault("retrieval", {})["top_k"] = top_k
        if include_scores is True:
            body.setdefault("return", {})["include_scores"] = True
        if cursor:
            body["cursor"] = cursor
        if trace is True:
            body.setdefault("return", {})["trace"] = True

        headers: Dict[str, str] = {}
        if self._agent_id:
            headers["X-Flumes-Agent"] = self._agent_id
        emit("request", method="POST", url="/v0/recall")
        resp = self._transport.recall(body, headers=headers)
        emit("response", status=200, url="/v0/recall", request_id=resp.get("request_id"))
        return resp

    def delete(self, memory_id: str) -> dict:
        return self._transport.delete(memory_id)

    def update(self, memory_id: str, *, memory: str, metadata: Optional[dict] = None) -> dict:
        payload = UpdateMemoryRequest(memory=memory, metadata=metadata).model_dump(mode="json")
        return self._transport.update(memory_id, payload)

    def get_all(
        self,
        *,
        entity_id: str,
        namespace: Optional[str] = None,
        type: Optional[str] = None,
        tag: Optional[str] = None,
        archived: Optional[bool] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict:
        ns = namespace or self._namespace
        params: Dict[str, Any] = {"entity_id": entity_id, "namespace": ns}
        if type:
            params["type"] = type
        if tag:
            params["tag"] = tag
        if archived is not None:
            params["archived"] = archived
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if sort:
            params["sort"] = sort
        if limit is not None:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        headers: Dict[str, str] = {}
        if self._agent_id:
            headers["X-Flumes-Agent"] = self._agent_id
        emit("request", method="GET", url="/v0/memories", params=params)
        resp = self._transport.memories_list(params, headers=headers)
        emit("response", status=200, url="/v0/memories", request_id=resp.get("request_id"))
        return resp

    # ------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------

    def health(self) -> dict:
        return self._transport.health()

    def meta(self) -> dict:
        return self._transport.meta()
