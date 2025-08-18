# custos/integrations/django.py
from __future__ import annotations
import json
from typing import Callable, Optional
from django.utils.deprecation import MiddlewareMixin

from ..bootstrap import custos_bootstrap
from ..client import AutoLoggingGuardian

def _json_loads(body: bytes) -> dict:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return {}

class CustosCaptureMiddleware(MiddlewareMixin):
    """
    Auto-captures (prompt, response) at the HTTP boundary.
    - No AI-model libraries required.
    - Reads request JSON to find a prompt key.
    - Reads response JSON to find a response key.

    Configure via env:
      CUSTOS_PROMPT_KEYS="prompt,input,message"
      CUSTOS_RESPONSE_KEYS="response,output,reply"
      CUSTOS_CAPTURE_PATHS="/chat,/api/chat,/chatbot1/chat"
    """
    def __init__(self, get_response: Callable):
        super().__init__(get_response)
        import os
        self.capture_paths = [p.strip() for p in os.getenv("CUSTOS_CAPTURE_PATHS", "/chat,/chatbot1/chat").split(",") if p.strip()]
        self.prompt_keys = [k.strip() for k in os.getenv("CUSTOS_PROMPT_KEYS", "prompt,input,message").split(",") if k.strip()]
        self.response_keys = [k.strip() for k in os.getenv("CUSTOS_RESPONSE_KEYS", "response,output,reply").split(",") if k.strip()]
        self.guardian: Optional[AutoLoggingGuardian] = custos_bootstrap()  # starts HRV if key present

    def process_request(self, request):
        request._custos_prompt_text = ""
        try:
            if any(request.path.startswith(p) for p in self.capture_paths) and getattr(request, "body", b""):
                data = _json_loads(request.body)
                if isinstance(data, dict):
                    for k in self.prompt_keys:
                        v = data.get(k)
                        if isinstance(v, str):
                            request._custos_prompt_text = v
                            break
        except Exception:
            pass  # never break the app

    def process_response(self, request, response):
        # Only attempt if we saw a prompt and have a guardian
        if not getattr(request, "_custos_prompt_text", "") or not self.guardian:
            return response
        try:
            body = getattr(response, "content", b"") or b""
            data = _json_loads(body)
            resp_text = ""
            if isinstance(data, dict):
                for k in self.response_keys:
                    v = data.get(k)
                    if isinstance(v, str):
                        resp_text = v
                        break
            if resp_text:
                # Non-blocking: let the guardian post a 'response' beat
                self.guardian.evaluate(request._custos_prompt_text, resp_text)
        except Exception:
            pass
        return response
