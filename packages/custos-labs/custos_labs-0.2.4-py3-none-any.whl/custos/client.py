# custos/client.py
from __future__ import annotations

import json
import threading
import time
import random
import requests
from typing import Optional, Dict, Any

from .config import CustosConfig

class AutoLoggingGuardian:
    """
    Zero-config HRV/beat poster (pure-Custos, no external model deps).

    Behavior:
      • Starts background 'heartbeat' beats so the simulator shows live HRV.
      • Optional: .evaluate(prompt, response) posts a 'response' beat.
      • No run_id needed — backend attaches to the active run for the API key.

    POST {backend_url}/simulator/logs/
      Body:
        kind: "heartbeat" | "response"
        prompt?: str
        response?: str
        confidence?: float
      Headers:
        Authorization: ApiKey <RAW_API_KEY>
    """

    def __init__(self, cfg: CustosConfig):
        self._cfg = cfg
        self._enabled = bool(cfg.api_key)
        self._session: Optional[requests.Session] = None
        self._stop = threading.Event()
        self._hb_thread: Optional[threading.Thread] = None

        if self._enabled:
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"ApiKey {cfg.api_key}",
                "Content-Type": "application/json",
            })
            if cfg.heartbeat_enabled:
                self.start_heartbeats()

    # -------- Public --------
    def start_heartbeats(self) -> None:
        if not self._enabled or self._hb_thread is not None:
            return
        self._hb_thread = threading.Thread(
            target=self._heartbeat_loop, name="custos-heartbeats", daemon=True
        )
        self._hb_thread.start()

    def stop_heartbeats(self) -> None:
        if self._hb_thread is None:
            return
        self._stop.set()
        try:
            self._hb_thread.join(timeout=2.0)
        except Exception:
            pass
        self._hb_thread = None
        self._stop.clear()

    def evaluate(self, prompt: str, response: str, confidence: float = 1.0) -> Dict[str, Any]:
        """
        Tie a model response to the simulator stream (optional).
        Fire-and-forget; network issues never crash the app.
        """
        if not self._enabled or self._session is None:
            return {"alignment_status": "skipped", "reason": "no_api_key"}

        payload = {
            "kind": "response",
            "prompt": prompt or "",
            "response": response or "",
            "confidence": float(confidence),
        }
        self._post_async(payload)
        return {"alignment_status": "sent"}

    # -------- Internals --------
    def _post_async(self, payload: dict) -> None:
        if not self._enabled or self._session is None:
            return

        def _send():
            try:
                self._session.post(
                    f"{self._cfg.backend_url}/simulator/logs/",
                    data=json.dumps(payload),
                    timeout=self._cfg.timeout_sec,
                )
            except Exception:
                # Silent by design — never break the user's app
                pass

        threading.Thread(target=_send, daemon=True).start()

    def _heartbeat_loop(self) -> None:
        """
        Emit 'heartbeat' beats until stopped.
        Adds tiny jitter so the HRV line visibly moves.
        """
        base_conf = 0.98
        interval = self._cfg.heartbeat_interval_sec or 2.0
        if interval <= 0:
            interval = 2.0

        while not self._stop.is_set():
            confidence = max(0.90, min(1.0, base_conf + random.uniform(-0.02, 0.02)))
            self._post_async({"kind": "heartbeat", "confidence": confidence})

            end_at = time.time() + interval
            while time.time() < end_at and not self._stop.is_set():
                time.sleep(0.1)

    def __del__(self):
        try:
            self.stop_heartbeats()
        except Exception:
            pass

