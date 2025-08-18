from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from handit_core import configure as _configure
from handit_core import entrypoint as _entrypoint
from handit_core import session as session

# Re-export FastAPI helpers for convenience
try:  # pragma: no cover
    from .fastapi import HanditMiddleware, use_fastapi  # type: ignore
except Exception:  # pragma: no cover
    HanditMiddleware = None  # type: ignore
    def use_fastapi(*args, **kwargs):  # type: ignore
        raise RuntimeError("fastapi is not installed; `pip install fastapi` to use handit_ai.use_fastapi")


def configure(**kwargs: Any) -> None:
    """Configure Handit (e.g., HANDIT_ENDPOINT, HANDIT_API_KEY, etc.)."""
    _configure(**kwargs)


def tracing(agent: str, capture: Optional[str] = None, attrs: Optional[Dict[str, str]] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to trace a function with a clear agent name.

    Example:
        @handit.tracing(agent="checkout")
        def handle(req): ...
    """
    return _entrypoint(tag=agent, capture=capture, attrs=attrs)


# Friendly alias
trace = tracing

