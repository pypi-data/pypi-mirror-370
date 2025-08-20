from __future__ import annotations

from typing import Optional, Dict, Any, Literal


FlumesErrorCode = Literal[
    "AUTH_INVALID_API_KEY",
    "RATE_LIMITED",
    "BUDGET_EXCEEDED",
    "ENTITY_NOT_FOUND",
    "VALIDATION_FAILED",
    "CONFLICT",
    "NOT_AUTHORIZED",
    "SERVER_DEGRADED",
    "TIMEOUT",
    "NETWORK",
    "BAD_REQUEST",
]


class FlumesError(Exception):
    """Base exception carrying stable error code and metadata."""

    def __init__(
        self,
        message: str,
        *,
        code: FlumesErrorCode,
        status: int,
        request_id: Optional[str] = None,
        retry_after_sec: Optional[int] = None,
        rate_limit_remaining: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.request_id = request_id
        self.retry_after_sec = retry_after_sec
        self.rate_limit_remaining = rate_limit_remaining
        self.details = details or {}

    def __str__(self) -> str:  # pragma: no cover
        rid = f" request_id={self.request_id}" if self.request_id else ""
        return f"[{self.code}] {super().__str__()} (status={self.status}{rid})"


# Backwards-compatible subclasses for older catch sites
class AuthenticationError(FlumesError):
    pass


class NotFoundError(FlumesError):
    pass


class RateLimitError(FlumesError):
    pass


class TransportError(FlumesError):
    pass
