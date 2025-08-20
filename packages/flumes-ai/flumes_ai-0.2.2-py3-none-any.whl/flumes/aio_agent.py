from __future__ import annotations

from typing import Optional, Dict

from flumes.aio_client import AsyncMemoryClient
from flumes.models import Message
from flumes.utils.openai_wrapper import LLMBackend, OpenAIBackend
from flumes.logger import emit


class AsyncAgent:
    """Async variant of :class:`flumes.agent.Agent`."""

    def __init__(
        self,
        *,
        agent_id: str,
        user_id: Optional[str] = None,
        run_id: Optional[str] = None,
        memory_client: Optional[AsyncMemoryClient] = None,
        llm_backend: Optional[LLMBackend] = None,
    ):
        self.agent_id = agent_id
        self.user_id = user_id
        self.run_id = run_id
        self._mem = memory_client or AsyncMemoryClient()
        self._llm = llm_backend or OpenAIBackend()

    # --------------------------------------------------
    async def remember(self, memory: str, *, metadata: Optional[Dict] = None):
        return await self._mem.add(
            messages=[Message(role="assistant", content=memory)],
            agent_id=self.agent_id,
            user_id=self.user_id,
            run_id=self.run_id,
            metadata=metadata,
            infer=False,
        )

    async def chat(self, prompt: str, *, limit: int = 20) -> str:  # noqa: D401
        await self._mem.add(
            messages=[Message(role="user", content=prompt)],
            agent_id=self.agent_id,
            user_id=self.user_id,
            run_id=self.run_id,
            infer=False,
        )

        mems = await self._mem.search(
            agent_id=self.agent_id,
            user_id=self.user_id,
            query=prompt,
            limit=limit,
        )

        context_lines = [m["memory"] for m in mems.get("memories", [])]
        system_msg = (
            "You are an AI assistant equipped with long-term memory. "
            "Relevant stored memories will be provided as context."
        )
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "system", "content": "\n\n".join(context_lines)},
            {"role": "user", "content": prompt},
        ]

        emit("llm.called", backend=self._llm.__class__.__name__, prompt=prompt)
        reply = await self._llm.acomplete(messages)

        await self._mem.add(
            messages=[Message(role="assistant", content=reply)],
            agent_id=self.agent_id,
            user_id=self.user_id,
            run_id=self.run_id,
            infer=True,
        )
        return reply
