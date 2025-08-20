from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Summarizer(ABC):
    """Interface for condensing a set of messages into a shorter memory blob."""

    @abstractmethod
    def summarize(self, messages: List[Dict[str, str]]) -> str:  # noqa: D401
        """Return a summary string for *messages*."""


class RetentionPolicy(ABC):
    """Interface for deciding which memories to keep or evict."""

    @abstractmethod
    def should_retain(self, memory: Dict[str, Any]) -> bool:  # noqa: D401
        """Return ``True`` to keep the memory, ``False`` to evict it."""
