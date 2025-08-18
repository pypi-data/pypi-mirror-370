# custos/autocapture.py
"""
Transport-level autocapture (no AI SDK deps).

We monkey-patch common HTTP clients (requests, httpx if present) to
inspect JSON request/response bodies and infer (prompt, response) pairs.
If those libs are NOT installed, this silently does nothing.

Extraction logic:
- Request JSON:
    * If 'messages' is a list of {role, content}, take last user content.
    * Else scan env-configured keys: CUSTOS_PROMPT_KEYS (default: prompt,input,message,query)
- Response JSON:
    * Try OpenAI-style: choices[0].message.content / choices[0].text
    * Try Ollama-style: message.content
    * Else scan env-configured keys: CUSTOS_RESPONSE_KEYS (default: response,output,reply,text,generated_text,summary_text)

We never import any AI model SDK.
"""

from __future__ import annotations
from typing import Any, Optional, Tuple
import os
import json

# ---------- helpers ----------

def _env_keys(name: str, default_csv: str) -> list[str]:
    raw = os.getenv(name, default_csv)
    return [k.strip() for k in raw.split(",") if k.strip()]

_PROMPT_KEYS = _env_keys("CUSTOS_PROMPT_KEYS", "prompt,input,message,query")
_RESPONSE_KEYS = _env_keys("CUSTOS_RESPONSE_KEYS", "response,output,reply,text,generated_text,summary_text")

def _safe_json(obj: Any) -> dict:
    # Accept dict, or attempt to parse bytes/str; else {}
    try:
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, (bytes, bytearray)):
            return json.loads(obj.decode("utf-8"))
        if isinstance(obj, str):
            return json.loads(obj)
    except Exception:
        pass
    return {}

def _extract_prompt(req_json: dict) -> str:
    # 1) OpenAI/Groq/OpenRouter style: messages -> last user
    try:
        msgs = req_json.get("messages")
        if isinstance(msgs, list):
            for m in reversed(msgs):
                if isinstance(m, dict) and m.get("role") == "user":
                    c = m.get("content", "")
                    if isinstance(c, str) and c.strip():
                        return c
    except Exception:
        pass

    # 2) Generic keys
    for k in _PROMPT_KEYS:
        v = req_json.get(k)
        if isinstance(v, str) and v.strip():
            return v

    return ""

def _extract_response(resp_json: dict) -> str:
    # 1) OpenAI chat style
    try:
        choices = resp_json.get("choices")
        if isinstance(choices, list) and choices:
            ch0 = choices[0]
            if isinstance(ch0, dict):
                # chat
                msg = ch0.get("message")
                if isinstance(msg, dict):
                    c = msg.get("content")
                    if isinstance(c, str) and c.strip():
                        return c
                # legacy text
                txt = ch0.get("text")
                if isinstance(txt, str) and txt.strip():
                    return txt
    except Exception:
        pass

    # 2) Ollama chat style
    try:
        msg = resp_json.get("message")
        if isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str) and c.strip():
                return c
    except Exception:
        pass

    # 3) Generic keys
    for k in _RESPONSE_KEYS:
        v = resp_json.get(k)
        if isinstance(v, str) and v.strip():
            return v

    return ""

def _maybe_eval(guardian: Any, req_json: dict, resp_json: dict) -> None:
    try:
        prompt = _extract_prompt(req_json)
        if not prompt:
            return
        reply = _extract_response(resp_json)
        if not reply:
            return
        # Non-blocking: guardian handles async posting
        guardian.evaluate(prompt, reply)
    except Exception:
        # Never break host app
        pass

# ---------- requests patch ----------

def _enable_requests(guardian: Any) -> None:
    try:
        import requests  # type: ignore
    except Exception:
        return

    # Patch Session.request so we catch all verbs + adapters
    orig_request = requests.Session.request

    def wrapped(self, method, url, **kwargs):
        req_json: dict = {}
        try:
            if "json" in kwargs:
                req_json = _safe_json(kwargs.get("json"))
            elif "data" in kwargs:
                req_json = _safe_json(kwargs.get("data"))
        except Exception:
            req_json = {}

        resp = orig_request(self, method, url, **kwargs)

        resp_json: dict = {}
        try:
            # Avoid consuming stream; requests caches .json() load
            resp_json = resp.json() if hasattr(resp, "json") else {}
        except Exception:
            resp_json = {}

        _maybe_eval(guardian, req_json, resp_json)
        return resp

    requests.Session.request = wrapped  # type: ignore

# ---------- httpx patch ----------

def _enable_httpx(guardian: Any) -> None:
    try:
        import httpx  # type: ignore
    except Exception:
        return

    # Patch Client.send to capture both sync client and high-level helpers
    orig_send = httpx.Client.send

    def wrapped(self, request, *args, **kwargs):
        req_json: dict = {}
        try:
            # httpx stores JSON on request extensions when using json= kw
            ext = getattr(request, "extensions", {}) or {}
            j = ext.get("json")
            if j is not None:
                req_json = _safe_json(j)
            else:
                # try body
                req_json = _safe_json(request.content)
        except Exception:
            req_json = {}

        resp = orig_send(self, request, *args, **kwargs)

        resp_json: dict = {}
        try:
            # Read safely without breaking further reads; httpx caches text
            text = resp.text  # triggers content load into memory
            resp_json = _safe_json(text)
        except Exception:
            resp_json = {}

        _maybe_eval(guardian, req_json, resp_json)
        return resp

    httpx.Client.send = wrapped  # type: ignore

# ---------- public entry ----------

def enable(guardian: Any) -> None:
    """
    Activate transport-level capture. Safe if libraries are absent.
    """
    _enable_requests(guardian)
    _enable_httpx(guardian)
