from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    url: str
    interval: float = 1.0
    count: Optional[int] = None
    timeout: float = 5.0
    method: str = "HEAD"
    include_body: bool = False
    mode: str = "interactive"  # interactive | json | plain

    # Alerting thresholds (in milliseconds)
    warn_threshold: Optional[float] = None
    crit_threshold: Optional[float] = None

    # Additional options
    keepalive: bool = True
    resolve_once: bool = False
    user_agent: Optional[str] = None
    auth: Optional[str] = None  # Format: "user:pass" or "bearer:token"
    insecure: bool = False
    export_file: Optional[str] = None
    show_percentiles: bool = False

    # Network options
    ipv4_only: bool = False
    ipv6_only: bool = False

    # UI options
    refresh_rate: float = 4.0
