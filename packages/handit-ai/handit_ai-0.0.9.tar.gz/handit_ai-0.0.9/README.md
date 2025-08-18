# Handit Core (Python)

Lightweight function and HTTP tracing for Python applications with zero configuration. Captures function calls/returns with arguments and return values, and outgoing HTTP requests/responses (including bodies) for `requests` and `httpx`. Events are buffered in-memory and written once at process exit to `handit_events.jsonl`.

## Install

Build from source (requires Rust and Python toolchain):

```bash
python -m pip install maturin
python -m maturin develop --release -m python/pyproject.toml
```

## Quick start

```python
from handit import session, tracing
import requests

@tracing(agent="demo")
def fetch_user(user_id: int) -> dict:
    resp = requests.get(f"https://httpbin.org/anything/{user_id}")
    return resp.json()

if __name__ == "__main__":
    with session(tag="demo-session"):
        fetch_user(42)
# Events will be written to ./handit_events.jsonl at exit
```

## What is captured
- Function events: call/return/exception
  - Arguments preview on call
  - Return value preview on return
- HTTP events (client-side)
  - requests/httpx: method, URL, headers, request body; response status, headers, body, size, duration, error
  - aiohttp: method, URL, headers; response status, headers (bodies are not captured by default)

## Behavior
- Zero-config: HTTP instrumentation is enabled on import; no environment variables are required.
- Noise reduction: internal library frames and stdlib/site-packages are excluded by default.
- Output: events are buffered and flushed once at exit to `handit_events.jsonl`.
  - Override path via env `HANDIT_OUTPUT_FILE=./path/file.jsonl`.

## Advanced
- Manual flush during runtime:
```python
from handit_core import handit_core_native as native
native.flush_events_to_file("./handit_events.jsonl")
```

- Optional envs (all have safe defaults):
  - `HANDIT_INCLUDE` / `HANDIT_EXCLUDE`: module/function regex filters
  - `HANDIT_MAX_STR` (default 256), `HANDIT_MAX_LOCALS` (default 64)
  - `HANDIT_REDACT`: regex for keys to redact in previews
  - `HANDIT_CAPTURE_ONLY_CWD` (default true)

## Notes
- Capturing full HTTP bodies may include sensitive data. Ensure you comply with your data policy.
- For `aiohttp` streamed bodies, body capture can be added with explicit buffering middleware if needed.
