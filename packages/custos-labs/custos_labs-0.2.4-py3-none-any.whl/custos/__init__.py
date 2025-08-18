# custos/__init__.py
from __future__ import annotations

__version__ = "0.2.4"

from .exceptions import AlignmentViolation
from .ethics import EthicsRegistry
from .training import FeedbackTrainer
from .guardian import CustosGuardian

# Public programmatic API (optional for users who want to drive it directly)
from .config import CustosConfig
from .client import AutoLoggingGuardian

__all__ = [
    "AlignmentViolation",
    "EthicsRegistry",
    "FeedbackTrainer",
    "CustosGuardian",
    "set_api_key",
    "set_backend_url",
    "guardian",
]

# Lightweight programmatic shim – not required if using Django integration.
_cfg = CustosConfig()

def set_api_key(raw_key: str) -> None:
    _cfg.api_key = raw_key

def set_backend_url(url: str) -> None:
    _cfg.backend_url = url.rstrip("/")

def guardian() -> AutoLoggingGuardian:
    """
    Returns an AutoLoggingGuardian bound to env/_cfg.
    Starts HRV heartbeats automatically (unless disabled by env).
    """
    return AutoLoggingGuardian(_cfg)
