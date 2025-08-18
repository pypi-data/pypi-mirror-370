# custos/config.py
from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import Optional

def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() not in ("0", "false", "no", "off")

@dataclass
class CustosConfig:
    # Read from env so users can configure without code
    api_key: Optional[str] = os.getenv("CUSTOS_API_KEY") or None
    backend_url: str = (os.getenv("CUSTOS_BACKEND_URL") or "https://custoslabs-backend.onrender.com").rstrip("/")
    timeout_sec: int = int(os.getenv("CUSTOS_TIMEOUT_SEC", "8"))

    # HRV / heartbeat controls
    heartbeat_enabled: bool = _env_bool("CUSTOS_HEARTBEATS", True)
    auto_heartbeat: bool = field(default_factory=lambda: os.getenv("CUSTOS_AUTO_HEARTBEAT", "1") in ("1","true","True"))
    heartbeat_interval_sec: float = float(os.getenv("CUSTOS_HEARTBEAT_INTERVAL", "2.0"))
