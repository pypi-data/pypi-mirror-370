from __future__ import annotations

import os
import sys
import time
import functools
import inspect
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, Optional

try:
    # Prefer package-local native module
    from . import handit_core_native as _native  # type: ignore
except Exception:
    try:
        # Fallback to top-level module name if installed globally
        import handit_core_native as _native  # type: ignore
    except Exception:  # pragma: no cover - not built yet
        _native = None  # type: ignore


def version() -> str:
    return "0.0.1"  # synced with Cargo.toml for now


# Async-friendly session state
_active_session_id: ContextVar[Optional[str]] = ContextVar("handit_active_session_id", default=None)

# Global config (merged from env + user)
_config: Dict[str, Any] = {}


def _merge_env_config(user_cfg: Dict[str, Any]) -> Dict[str, Any]:
    env_map = {
        "HANDIT_ENDPOINT": "https://handit-api-oss-299768392189.us-central1.run.app/api/ingest/events",
        "HANDIT_API_KEY": os.getenv("HANDIT_API_KEY"),
        "HANDIT_SAMPLE_RATE": os.getenv("HANDIT_SAMPLE_RATE"),
        "HANDIT_CAPTURE": os.getenv("HANDIT_CAPTURE"),
        "HANDIT_MAX_STR": os.getenv("HANDIT_MAX_STR"),
        "HANDIT_MAX_LOCALS": os.getenv("HANDIT_MAX_LOCALS"),
        "HANDIT_INCLUDE": os.getenv("HANDIT_INCLUDE"),
        "HANDIT_EXCLUDE": os.getenv("HANDIT_EXCLUDE"),
        "HANDIT_REDACT": os.getenv("HANDIT_REDACT"),
        "HANDIT_OTEL": os.getenv("HANDIT_OTEL"),
        "HANDIT_SPOOL_DIR": os.getenv("HANDIT_SPOOL_DIR"),
    }
    merged = {k: v for k, v in env_map.items() if v is not None}
    merged.update(user_cfg)
    return merged


def configure(**kwargs: Any) -> None:
    global _config
    cfg = _merge_env_config(kwargs)
    # Minimal validation
    if "HANDIT_ENDPOINT" in cfg and not isinstance(cfg["HANDIT_ENDPOINT"], str):
        raise ValueError("HANDIT_ENDPOINT must be a string")
    # Coerce numeric caps
    if "HANDIT_MAX_STR" in cfg:
        cfg["HANDIT_MAX_STR"] = int(cfg["HANDIT_MAX_STR"])
    if "HANDIT_MAX_LOCALS" in cfg:
        cfg["HANDIT_MAX_LOCALS"] = int(cfg["HANDIT_MAX_LOCALS"])
    # Propagate HANDIT_* settings into process environment before native Lazy reads them
    for k, v in list(cfg.items()):
        if k.startswith("HANDIT_") and v is not None:
            os.environ[k] = str(v)
    _config = cfg
    # Enable HTTP instrumentation by default
    try:
        from .http_instrumentation import patch_requests, patch_httpx, patch_aiohttp
        patch_requests(); patch_httpx(); patch_aiohttp()
    except Exception:
        pass
    # Push API settings to native exporter if provided
    try:
        endpoint = cfg.get("HANDIT_ENDPOINT")
        api_key = cfg.get("HANDIT_API_KEY")
        if _native is not None and (endpoint is not None or api_key is not None):
            set_http = getattr(_native, "set_http_config_py", None)
            if callable(set_http):
                set_http(endpoint, api_key)
    except Exception:
        pass


@contextmanager
def session(tag: Optional[str] = None, capture: Optional[str] = None, traceparent: Optional[str] = None, attrs: Optional[Dict[str, str]] = None):
    attrs = attrs or {}
    # Start session via native module and activate native profiler
    if _native is None:
        raise RuntimeError("handit_core native extension not built")
    session_id = _native.start_session_py(tag, attrs, traceparent, None)
    token = _active_session_id.set(session_id)
    _native.start_profiler_py(session_id)
    try:
        yield
    finally:
        _native.stop_profiler_py()
        _active_session_id.reset(token)
        # end_session would be added later


def entrypoint(tag: Optional[str] = None, capture: Optional[str] = None, attrs: Optional[Dict[str, str]] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrapper(*args: Any, **kwargs: Any):
                with session(tag=tag, capture=capture, attrs=attrs):
                    result = await fn(*args, **kwargs)
                    return result
            return awrapper
        else:
            @functools.wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                with session(tag=tag, capture=capture, attrs=attrs):
                    return fn(*args, **kwargs)
            return wrapper
    return decorator


# Minimal public API for manual calls from Python for early testing
if _native is not None:
    start_session = _native.start_session_py
    on_call = _native.on_call_py
    on_return = _native.on_return_py
    on_exception = _native.on_exception_py
else:
    def start_session(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_call(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_return(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_exception(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")


# Auto-enable HTTP instrumentation on import for zero-config usage
try:
    from .http_instrumentation import patch_requests, patch_httpx, patch_aiohttp
    patch_requests(); patch_httpx(); patch_aiohttp()
except Exception:
    pass

# Auto-enable OpenAI instrumentation
try:
    from .openai_instrumentation import patch_openai
    patch_openai()
except Exception:
    pass

# Write all buffered events to file at process exit, default path
try:
    import atexit
    def _flush_at_exit() -> None:
        try:
            if _native is not None:
                flush = getattr(_native, "flush_events_to_file", None)
                if callable(flush):
                    path = os.getenv("HANDIT_OUTPUT_FILE", "./handit_events.jsonl")
                    flush(path)
        except Exception:
            pass
    atexit.register(_flush_at_exit)
except Exception:
    pass

