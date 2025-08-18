from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
	from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover
	_native = None  # type: ignore

from . import _active_session_id  # type: ignore

REDACT_QUERY = True
DEFAULT_TIMEOUT = 5.0  # seconds


def _emit_request(method: str, url: str, headers: Optional[Dict[str, Any]], bytes_out: Optional[int], request_body: Optional[str]) -> int:
	sid = _active_session_id.get()
	if not sid or _native is None:
		return 0
	t0 = time.time_ns()
	_native_on = getattr(_native, "on_http_request_py", None)
	if _native_on is None:
		return 0
	_native_on(sid, method, url, t0, headers or {}, bytes_out or 0, request_body)
	return t0


def _emit_response(t0_ns: int, status: int, headers: Optional[Dict[str, Any]], bytes_in: Optional[int], error: Optional[str], response_body: Optional[str]) -> None:
	sid = _active_session_id.get()
	if not sid or _native is None:
		return
	t1 = time.time_ns()
	_native_off = getattr(_native, "on_http_response_py", None)
	if _native_off is None:
		return
	_native_off(sid, status, t1, t1 - t0_ns, headers or {}, bytes_in or 0, error, response_body)


# requests instrumentation

def patch_requests() -> None:
	try:
		import requests
		from requests.sessions import Session
		from requests import Timeout
	except Exception:
		return

	# Prevent double patching
	if getattr(Session.request, "_handit_patched", False):
		return

	orig = Session.request

	def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Set a default timeout if not provided
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = DEFAULT_TIMEOUT
		# Extract request body (best-effort)
		body_str = None
		data = kwargs.get("data")
		json_data = kwargs.get("json")
		if json_data is not None:
			try:
				import json as _json
				body_str = _json.dumps(json_data)
			except Exception:
				body_str = str(json_data)
		elif data is not None:
			try:
				if isinstance(data, (bytes, bytearray)):
					body_str = data.decode("utf-8", errors="replace")
				else:
					body_str = str(data)
			except Exception:
				body_str = "<unrepr>"
		t0 = _emit_request(method, url, kwargs.get("headers"), None, body_str)
		# Suppress profiler while executing the HTTP client's internals
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = orig(self, method, url, *args, **kwargs)
			resp_body = None
			try:
				content = getattr(resp, "content", None)
				if content is not None:
					resp_body = content.decode("utf-8", errors="replace") if isinstance(content, (bytes, bytearray)) else str(content)
			except Exception:
				resp_body = "<unrepr>"
			_emit_response(t0, resp.status_code, dict(resp.headers), len(getattr(resp, "content", b"")) if getattr(resp, "content", None) is not None else None, None, resp_body)
			return resp
		except Timeout as e:
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	Session.request = wrapped  # type: ignore


# httpx instrumentation (sync only here)

def patch_httpx() -> None:
	try:
		import httpx
	except Exception:
		return

	# Patch sync client
	if not getattr(httpx.Client.request, "_handit_patched", False):
		_patch_httpx_sync()
	
	# Patch async client  
	if not getattr(httpx.AsyncClient.request, "_handit_patched", False):
		_patch_httpx_async()


def _patch_httpx_sync() -> None:
	import httpx
	orig = httpx.Client.request

	def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Respect existing timeouts; set a default if none
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = httpx.Timeout(DEFAULT_TIMEOUT)
		# Extract httpx request body
		body_str = None
		content = kwargs.get("content")
		json_data = kwargs.get("json")
		data = kwargs.get("data")
		if json_data is not None:
			try:
				import json as _json
				body_str = _json.dumps(json_data)
			except Exception:
				body_str = str(json_data)
		elif content is not None:
			try:
				body_str = content.decode("utf-8", errors="replace") if isinstance(content, (bytes, bytearray)) else str(content)
			except Exception:
				body_str = "<unrepr>"
		elif data is not None:
			try:
				body_str = data.decode("utf-8", errors="replace") if isinstance(data, (bytes, bytearray)) else str(data)
			except Exception:
				body_str = "<unrepr>"
		t0 = _emit_request(method, str(url), kwargs.get("headers"), None, body_str)
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = orig(self, method, url, *args, **kwargs)
			resp_body = None
			try:
				if hasattr(resp, "content"):
					resp_body = resp.content.decode("utf-8", errors="replace") if isinstance(resp.content, (bytes, bytearray)) else str(resp.content)
			except Exception:
				resp_body = "<unrepr>"
			_emit_response(t0, resp.status_code, dict(resp.headers), len(resp.content) if hasattr(resp, "content") else None, None, resp_body)
			return resp
		except httpx.TimeoutException as e:
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	httpx.Client.request = wrapped  # type: ignore


def _patch_httpx_async() -> None:
	import httpx
	orig = httpx.AsyncClient.request

	async def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Respect existing timeouts; set a default if none
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = httpx.Timeout(DEFAULT_TIMEOUT)
		# Extract httpx request body
		body_str = None
		content = kwargs.get("content")
		json_data = kwargs.get("json")
		data = kwargs.get("data")
		if json_data is not None:
			try:
				import json as _json
				body_str = _json.dumps(json_data)
			except Exception:
				body_str = str(json_data)
		elif content is not None:
			try:
				body_str = content.decode("utf-8", errors="replace") if isinstance(content, (bytes, bytearray)) else str(content)
			except Exception:
				body_str = "<unrepr>"
		elif data is not None:
			try:
				body_str = data.decode("utf-8", errors="replace") if isinstance(data, (bytes, bytearray)) else str(data)
			except Exception:
				body_str = "<unrepr>"
		t0 = _emit_request(method, str(url), kwargs.get("headers"), None, body_str)
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = await orig(self, method, url, *args, **kwargs)
			resp_body = None
			try:
				if hasattr(resp, "content"):
					resp_body = resp.content.decode("utf-8", errors="replace") if isinstance(resp.content, (bytes, bytearray)) else str(resp.content)
			except Exception:
				resp_body = "<unrepr>"
			_emit_response(t0, resp.status_code, dict(resp.headers), len(resp.content) if hasattr(resp, "content") else None, None, resp_body)
			return resp
		except httpx.TimeoutException as e:
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	httpx.AsyncClient.request = wrapped  # type: ignore


# aiohttp basic instrumentation (only wrap _request)

def patch_aiohttp() -> None:
	try:
		import aiohttp
		import asyncio  # for TimeoutError reference
	except Exception:
		return

	# Prevent double patching
	if getattr(aiohttp.ClientSession._request, "_handit_patched", False):
		return

	orig = aiohttp.ClientSession._request

	async def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Set default timeout if not provided
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
		# For aiohttp we cannot read the request body here reliably; leave as None
		t0 = _emit_request(method, str(url), kwargs.get("headers"), None, None)
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = await orig(self, method, url, *args, **kwargs)
			try:
				# consume headers only; body not read here
				# To avoid consuming the stream, don't read body here. Users can opt in with middleware later.
				_emit_response(t0, resp.status, dict(resp.headers), None, None, None)
			except Exception:  # pragma: no cover
				pass
			return resp
		except asyncio.TimeoutError as e:  # type: ignore[name-defined]
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_profiler_exit = _suppress_exit
					_suppress_profiler_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	aiohttp.ClientSession._request = wrapped  # type: ignore