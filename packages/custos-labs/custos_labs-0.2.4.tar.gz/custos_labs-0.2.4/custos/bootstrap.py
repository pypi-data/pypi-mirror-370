# custos/bootstrap.py
from __future__ import annotations
import threading
from .config import CustosConfig
from .client import AutoLoggingGuardian

_guardian_lock = threading.Lock()
_guardian_singleton: AutoLoggingGuardian | None = None

def custos_bootstrap() -> AutoLoggingGuardian | None:
    """
    Bootstraps Custos from ENV only.
    Returns the AutoLoggingGuardian singleton (or None if no API key).
    """
    global _guardian_singleton
    cfg = CustosConfig()
    if not cfg.api_key:
        return None

    with _guardian_lock:
        if _guardian_singleton is None:
            _guardian_singleton = AutoLoggingGuardian(cfg)
    return _guardian_singleton
