from __future__ import annotations

from typing import List, Dict, Any

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    openai = None  # noqa


class LLMBackend:
    """Abstract interface for chat completion backends."""

    async def acomplete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        raise NotImplementedError

    def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        raise NotImplementedError


class OpenAIBackend(LLMBackend):
    """Thin wrapper around ``openai.ChatCompletion`` for MVP."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        if openai is None:
            raise RuntimeError("openai package not installed; run `pip install openai`. ")
        self.model = model
        self.temperature = temperature

    def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:  # noqa: D401
        # Support both openai<1 (legacy) and >=1 (new client)
        try:
            from importlib.metadata import version as _pkg_version  # Python 3.8+

            ver = _pkg_version("openai")
        except Exception:
            ver = "0"

        if ver.startswith("0.") or ver.startswith("0"):
            # Legacy 0.x interface
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                **kwargs,
            )
            return resp.choices[0].message["content"]  # type: ignore[index]

        # 1.x interface – use typed client
        try:
            client = openai.OpenAI()
        except AttributeError:
            # Fallback for early 1.x
            client = openai.Client()

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
        client = openai.AsyncOpenAI()
        resp = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **kwargs,
        )
        return resp.choices[0].message.content
