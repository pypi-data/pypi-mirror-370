from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Callable, Optional

_logger = logging.getLogger("flumes")
_logger.setLevel(logging.INFO)


_on_request: Optional[Callable[..., None]] = None
_on_response: Optional[Callable[..., None]] = None
_on_error: Optional[Callable[..., None]] = None


def on_request(cb: Callable[..., None]) -> None:
    global _on_request
    _on_request = cb


def on_response(cb: Callable[..., None]) -> None:
    global _on_response
    _on_response = cb


def on_error(cb: Callable[..., None]) -> None:
    global _on_error
    _on_error = cb


def emit(event: str, **data: Any) -> None:
    """Emit a structured event.

    For the MVP this just prints a JSON line to stdout and logs via the
    ``logging`` module.  Down the line we can swap this for OpenTelemetry or
    any other sink.
    """
    payload: Dict[str, Any] = {
        "ts": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "event": event,
        "data": data,
    }

    # Print for immediate visibility
    print(json.dumps(payload, ensure_ascii=False))

    # Also forward to python logging for app-level collection
    _logger.debug(payload)

    # Fire hooks (non-fatal)
    try:
        if event == "request" and _on_request:
            _on_request(**data)
        elif event == "response" and _on_response:
            _on_response(**data)
        elif event == "error" and _on_error:
            _on_error(**data)
    except Exception:
        pass
