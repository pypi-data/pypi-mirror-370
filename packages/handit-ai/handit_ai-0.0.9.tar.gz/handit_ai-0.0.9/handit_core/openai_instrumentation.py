"""OpenAI instrumentation to capture high-level API calls."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
    from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover
    _native = None  # type: ignore

from . import _active_session_id  # type: ignore

import json, dataclasses, base64
from decimal import Decimal
from uuid import UUID
from datetime import date, datetime

def to_jsonable(x):
    # Pydantic v2 (OpenAI v1+)
    if hasattr(x, "model_dump"):
        return x.model_dump()
    # Pydantic v1 / common libs
    if hasattr(x, "dict"):
        return x.dict()
    # Dataclasses
    if dataclasses.is_dataclass(x):
        return dataclasses.asdict(x)
    # Built-ins
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, (list, tuple, set, frozenset)):
        return [to_jsonable(v) for v in x]
    if isinstance(x, dict):
        return {str(k): to_jsonable(v) for k, v in x.items()}
    # Common non-JSON types
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if isinstance(x, (UUID, Decimal)):
        return str(x)
    if isinstance(x, (bytes, bytearray)):
        return base64.b64encode(x).decode("utf-8")
    # Last resort
    if hasattr(x, "__dict__"):
        return {k: to_jsonable(v) for k, v in vars(x).items()}
    return str(x)

def to_json_string(obj) -> str:
    return json.dumps(to_jsonable(obj), ensure_ascii=False, separators=(",", ":"))

def patch_openai() -> None:
    """Patch OpenAI to emit custom events for API calls"""
    try:
        import openai
        from openai.resources.chat import completions
    except Exception:
        return
    
    # Prevent double patching
    if getattr(completions.Completions.create, "_handit_patched", False):
        return
    
    orig_create = completions.Completions.create
    
    def wrapped_create(self, **kwargs):  # type: ignore[no-untyped-def]
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])
        
        # Extract other params for logging (avoid **kwargs conflict)
        other_params = {k: v for k, v in kwargs.items() if k not in ["model", "messages"]}
        params = {
            "model": model,
            "messages": messages,
            **other_params
        }
        # Emit call event
        _native_on = getattr(_native, "on_call_with_args_py", None)
        _return_on = getattr(_native, "on_return_with_preview_py", None)
        if _native_on is None or _return_on is None:
            return
        sid = _active_session_id.get()
        if not sid or _native is None:
            return 0
        
        func_name = "create"  # Just "create"
        module_name = "openai.resources.chat.completions"
        file_name = "<openai-api>"
        line_no = 1
        t0 = time.time_ns()
        print(f"DEBUG: Emitting call event with params: {params}")

        if isinstance(params, dict):
            params_dict = params
        else:
            params_dict = params.to_dict()

        params_json = to_json_string(params_dict)

        _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
        
        try:
            # Make the actual call
            result = orig_create(self, **kwargs)
            print(f"DEBUG: Result: {result}")
            
            # Emit return event
            t1 = time.time_ns()
            dt_ns = t1 - t0
            result_json = to_json_string(result)
            _return_on(sid, func_name, t1, dt_ns, result_json)
            
            return result
            
        except Exception as e:
            raise
    
    setattr(wrapped_create, "_handit_patched", True)
    setattr(wrapped_create, "_handit_orig", orig_create)
    completions.Completions.create = wrapped_create  # type: ignore
