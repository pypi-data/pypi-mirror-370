from __future__ import annotations

from typing import List, Optional, Dict

from flumes.client import MemoryClient
from flumes.models import Message
from flumes.utils.openai_wrapper import LLMBackend, OpenAIBackend
from flumes.logger import emit


class Agent:
    """Chat agent powered by Flumes context assemble + OpenAI (optional)."""

    def __init__(
        self,
        *,
        agent_id: str,
        entity_id: Optional[str] = None,
        run_id: Optional[str] = None,
        memory_client: Optional[MemoryClient] = None,
        llm_backend: Optional[LLMBackend] = None,
    ):
        self.agent_id = agent_id
        self.entity_id = entity_id
        self.run_id = run_id
        self._mem = memory_client or MemoryClient(agent_id=agent_id)
        self._llm = llm_backend or OpenAIBackend()

    # --------------------------------------------------------
    # Memory helpers
    # --------------------------------------------------------

    def remember(self, memory: str, *, namespace: Optional[str] = None, metadata: Optional[Dict] = None) -> dict:
        """Store an assistant memory via context assemble ingest (event)."""
        return self._mem.add(
            input=memory,
            entity_id=self.entity_id or "anonymous",
            namespace=namespace,
        )

    # --------------------------------------------------------
    # Chat API
    # --------------------------------------------------------

    def chat(self, prompt: str, *, namespace: Optional[str] = None, retrieval: Optional[Dict] = None) -> str:  # noqa: D401
        """One-shot chat: assemble context (ingests user turn), call LLM, store reply."""
        # 1) Assemble context and ingest the user turn
        ctx = self._mem.add(
            input=prompt,
            entity_id=self.entity_id or "anonymous",
            namespace=namespace,
            retrieval=retrieval or {"preset": "factual"},
            include_snippet=True,
            return_structured_facts=True,
        )
        context = ctx.get("context", {})
        summary = context.get("summary") or ""
        facts = context.get("facts_struct", []) or context.get("facts", [])
        recent = context.get("recent_events", [])
        sources = context.get("sources", [])

        # 2) Build messages for the LLM
        sys = "You are a helpful assistant. Use the provided memory context when relevant."
        def fmt_fact(f):
            if isinstance(f, dict):
                subj = f.get("subject") or ""
                pred = f.get("predicate") or ""
                obj = f.get("object_text") or f.get("object_num") or ""
                return f"- {subj} {pred} {obj}".strip()
            return f"- {f}"
        mem_lines = [fmt_fact(f) for f in facts] + [f"- {e}" for e in recent]
        mem_block = "\n".join(mem_lines)
        messages = [
            {"role": "system", "content": sys},
            {"role": "system", "content": f"Summary:\n{summary}\n\nContext:\n{mem_block}"},
            {"role": "user", "content": prompt},
        ]

        # 3) Call LLM
        emit("llm.called", backend=self._llm.__class__.__name__, prompt=prompt)
        reply = self._llm.complete(messages)

        # 4) Store assistant reply (as event)
        self._mem.add(
            input=reply,
            entity_id=self.entity_id or "anonymous",
            namespace=namespace,
        )
        return reply
