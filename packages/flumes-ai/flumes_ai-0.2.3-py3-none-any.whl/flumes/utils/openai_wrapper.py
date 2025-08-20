from __future__ import annotations

from typing import List, Dict, Any
from types import ModuleType
import importlib

# Lazy import: avoid binding to a missing openai module at import time.
# We will import it when the backend is instantiated, so notebooks can
# `%pip install openai` right before creating the Agent without reloads.
openai: ModuleType | None = None


class LLMBackend:
    """Abstract interface for chat completion backends."""

    async def acomplete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        raise NotImplementedError

    def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        raise NotImplementedError


class OpenAIBackend(LLMBackend):
    """Thin wrapper around ``openai.ChatCompletion`` for MVP."""

    def __init__(self, *, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.2):
        global openai
        if openai is None:
            try:
                openai = importlib.import_module("openai")  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError("openai package not installed; run `pip install openai`.") from exc
        if not api_key or api_key == "your-openai-key":
            raise RuntimeError("OpenAI API key is required; pass api_key to OpenAIBackend or provide llm_backend.")
        self.model = model
        self.temperature = temperature
        self._api_key = api_key

    def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        # Support both openai<1 (legacy) and >=1 (new client)
        try:
            from importlib.metadata import version as _pkg_version  # Python 3.8+

            ver = _pkg_version("openai")
        except Exception:
            ver = "0"

        if ver.startswith("0.") or ver.startswith("0"):
            # Legacy 0.x interface
            openai.api_key = self._api_key  # type: ignore[attr-defined]
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                **kwargs,
            )
            return resp.choices[0].message["content"]  # type: ignore[index]

        # 1.x interface – use typed client
        try:
            client = openai.OpenAI(api_key=self._api_key)
        except AttributeError:
            # Fallback for early 1.x
            client = openai.Client(api_key=self._api_key)

        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **kwargs,
        )
        return resp.choices[0].message.content  # type: ignore[attr-defined]

    async def acomplete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        # Very lightweight async wrapper – supports 0.x and >=1.x
        try:
            from importlib.metadata import version as _pkg_version
            ver = _pkg_version("openai")
        except Exception:
            ver = "0"

        if ver.startswith("0.") or ver.startswith("0"):
            resp = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                **kwargs,
            )
            return resp.choices[0].message["content"]

        # 1.x async client
        client = openai.AsyncOpenAI(api_key=self._api_key)
        resp = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **kwargs,
        )
        return resp.choices[0].message.content
