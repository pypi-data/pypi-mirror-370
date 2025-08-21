import asyncio
import socket
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional
from urllib.parse import urlparse

import httpx

from .config import Config


@dataclass
class ProbePhases:
    dns: Optional[float]
    connect: Optional[float]
    tls: Optional[float]
    request_write: Optional[float]
    ttfb: Optional[float]
    body_read: Optional[float]
    total: float


@dataclass
class ProbeResult:
    ts: float
    seq: int
    latency_ms: float
    status_code: Optional[int]
    error: Optional[str]
    bytes_read: int
    content_type: Optional[str]
    host_address: Optional[str]
    anomaly: bool = False  # Will be set by metrics during update
    phases: Optional[ProbePhases] = None  # Phase breakdown when available

    def to_dict(self):  # serialization helper
        result = {
            "ts": self.ts,
            "seq": self.seq,
            "latency_ms": self.latency_ms,
            "status": self.status_code,
            "error": self.error,
            "bytes": self.bytes_read,
            "content_type": self.content_type,
            "host_address": self.host_address,
            "anomaly": self.anomaly,
        }
        if self.phases:
            result["phases"] = {
                "dns": self.phases.dns,
                "connect": self.phases.connect,
                "tls": self.phases.tls,
                "request_write": self.phases.request_write,
                "ttfb": self.phases.ttfb,
                "body_read": self.phases.body_read,
                "total": self.phases.total,
            }
        return result


async def resolve_hostname_with_timing(
    hostname: str, cfg: Config
) -> tuple[Optional[str], Optional[float], Optional[str]]:
    """Resolve hostname with timing and address family selection.

    Returns: (resolved_ip, dns_time_ms, error)
    """
    if not hostname:
        return None, None, None

    start_dns = time.monotonic_ns()
    try:
        # Determine address family
        family = socket.AF_UNSPEC  # Default: allow both IPv4 and IPv6
        if cfg.ipv4_only:
            family = socket.AF_INET
        elif cfg.ipv6_only:
            family = socket.AF_INET6

        # Resolve hostname
        loop = asyncio.get_event_loop()
        try:
            result = await loop.getaddrinfo(
                hostname, None, family=family, type=socket.SOCK_STREAM
            )
            if result:
                resolved_ip = result[0][4][0]  # First result's IP address
                end_dns = time.monotonic_ns()
                dns_time_ms = (end_dns - start_dns) / 1_000_000.0
                return resolved_ip, dns_time_ms, None
            else:
                return None, None, "NoAddressFound"
        except socket.gaierror as e:
            return None, None, f"DNSError:{e.strerror}"
    except Exception as e:
        return None, None, f"DNSError:{e.__class__.__name__}"


async def probe_tcp_once(
    cfg: Config, seq: int, hostname: str, port: int, resolved_ip: Optional[str] = None
) -> ProbeResult:
    """Probe TCP connection timing.

    Args:
        cfg: Configuration
        seq: Sequence number
        hostname: Target hostname
        port: Target port
        resolved_ip: Pre-resolved IP address (optional)

    Returns:
        ProbeResult with TCP connection timing
    """
    overall_start = time.monotonic_ns()
    error = None
    host_address = None

    # Initialize phase timings
    dns_time: Optional[float] = None
    connect_time: Optional[float] = None

    try:
        # DNS resolution timing (if not already resolved)
        target_ip = resolved_ip
        if not resolved_ip:
            target_ip, dns_time, dns_error = await resolve_hostname_with_timing(
                hostname, cfg
            )
            if dns_error:
                error = dns_error
                end_overall = time.monotonic_ns()
                latency_ms = (end_overall - overall_start) / 1_000_000.0
                phases = ProbePhases(
                    dns=dns_time,
                    connect=None,
                    tls=None,
                    request_write=None,
                    ttfb=None,
                    body_read=None,
                    total=latency_ms,
                )
                return ProbeResult(
                    ts=time.time(),
                    seq=seq,
                    latency_ms=latency_ms,
                    status_code=None,
                    error=error,
                    bytes_read=0,
                    content_type=None,
                    host_address=None,
                    phases=phases,
                )

        if not target_ip:
            error = "NoIPResolved"
            end_overall = time.monotonic_ns()
            latency_ms = (end_overall - overall_start) / 1_000_000.0
            phases = ProbePhases(
                dns=dns_time,
                connect=None,
                tls=None,
                request_write=None,
                ttfb=None,
                body_read=None,
                total=latency_ms,
            )
            return ProbeResult(
                ts=time.time(),
                seq=seq,
                latency_ms=latency_ms,
                status_code=None,
                error=error,
                bytes_read=0,
                content_type=None,
                host_address=None,
                phases=phases,
            )

        # Set host address for display
        host_address = (
            f"{hostname} ({target_ip})" if hostname != target_ip else target_ip
        )

        # TCP connection timing
        connect_start = time.monotonic_ns()
        try:
            # Create connection with timeout
            future = asyncio.open_connection(target_ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=cfg.timeout)
            connect_end = time.monotonic_ns()
            connect_time = (connect_end - connect_start) / 1_000_000.0

            # Close connection immediately
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass  # Ignore close errors

        except asyncio.TimeoutError:
            error = "ConnectionTimeout"
        except ConnectionRefusedError:
            error = "ConnectionRefused"
        except OSError as e:
            error = f"OSError:{e.strerror if hasattr(e, 'strerror') else str(e)}"
        except Exception as e:
            error = f"TCPError:{e.__class__.__name__}"

    except Exception as e:
        error = f"UnexpectedError:{e.__class__.__name__}"

    end_overall = time.monotonic_ns()
    total_latency_ms = (end_overall - overall_start) / 1_000_000.0

    phases = ProbePhases(
        dns=dns_time,
        connect=connect_time,
        tls=None,  # No TLS for plain TCP
        request_write=None,
        ttfb=None,
        body_read=None,
        total=total_latency_ms,
    )

    # For TCP, we use a pseudo status code: 0 for success, None for error
    status_code = 0 if not error else None

    return ProbeResult(
        ts=time.time(),
        seq=seq,
        latency_ms=total_latency_ms,
        status_code=status_code,
        error=error,
        bytes_read=0,
        content_type="tcp/connection" if not error else None,
        host_address=host_address,
        phases=phases,
    )


async def probe_once(
    client: httpx.AsyncClient,
    cfg: Config,
    seq: int,
    url: str,
    resolved_ip: Optional[str] = None,
) -> ProbeResult:
    overall_start = time.monotonic_ns()
    error = None
    status_code: Optional[int] = None
    bytes_read = 0
    content_type: Optional[str] = None
    host_address: Optional[str] = None

    # Initialize phase timings
    dns_time: Optional[float] = None
    connect_time: Optional[float] = None
    tls_time: Optional[float] = None
    request_write_time: Optional[float] = None
    ttfb_time: Optional[float] = None
    body_read_time: Optional[float] = None

    try:
        # Parse URL to get hostname
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        # DNS resolution timing (if not already resolved)
        actual_ip = resolved_ip
        if not resolved_ip and hostname:
            actual_ip, dns_time, dns_error = await resolve_hostname_with_timing(
                hostname, cfg
            )
            if dns_error:
                error = dns_error
                end_overall = time.monotonic_ns()
                latency_ms = (end_overall - overall_start) / 1_000_000.0
                phases = ProbePhases(
                    dns=dns_time,
                    connect=None,
                    tls=None,
                    request_write=None,
                    ttfb=None,
                    body_read=None,
                    total=latency_ms,
                )
                return ProbeResult(
                    ts=time.time(),
                    seq=seq,
                    latency_ms=latency_ms,
                    status_code=status_code,
                    error=error,
                    bytes_read=bytes_read,
                    content_type=content_type,
                    host_address=host_address,
                    phases=phases,
                )

        # Perform HTTP request
        request_start = time.monotonic_ns()
        r = await client.request(cfg.method, url)
        response_received = time.monotonic_ns()

        status_code = r.status_code
        content_type = r.headers.get("content-type")

        # Calculate TTFB (Time to First Byte) - time from request start to response headers
        ttfb_time = (response_received - request_start) / 1_000_000.0

        # Format host address
        if hostname and actual_ip and hostname != actual_ip:
            host_address = f"{hostname} ({actual_ip})"
        elif hostname:
            host_address = hostname
        elif actual_ip:
            host_address = actual_ip

        # Handle body reading if needed
        body_start = (
            time.monotonic_ns() if (cfg.include_body or cfg.method != "HEAD") else None
        )
        if cfg.include_body or cfg.method != "HEAD":
            content = r.content  # bytes
            bytes_read = len(content)
            body_end = time.monotonic_ns()
            body_read_time = (
                (body_end - body_start) / 1_000_000.0 if body_start else None
            )

    except Exception as e:
        # Classify error types
        error_name = e.__class__.__name__
        if "timeout" in str(e).lower() or error_name in [
            "ReadTimeout",
            "ConnectTimeout",
            "TimeoutException",
        ]:
            error = "Timeout"
        elif error_name in ["ConnectError", "ConnectionRefused"]:
            error = "ConnectRefused"
        elif (
            "ssl" in str(e).lower()
            or "tls" in str(e).lower()
            or error_name in ["SSLError"]
        ):
            error = "TLSError"
        else:
            error = error_name

    end_overall = time.monotonic_ns()
    total_latency_ms = (end_overall - overall_start) / 1_000_000.0

    # Create phases object
    phases = ProbePhases(
        dns=dns_time,
        connect=connect_time,  # TODO: Need custom transport to measure this accurately
        tls=tls_time,  # TODO: Need custom transport to measure this accurately
        request_write=request_write_time,  # TODO: Need custom transport to measure this accurately
        ttfb=ttfb_time,
        body_read=body_read_time,
        total=total_latency_ms,
    )

    return ProbeResult(
        ts=time.time(),
        seq=seq,
        latency_ms=total_latency_ms,
        status_code=status_code,
        error=error,
        bytes_read=bytes_read,
        content_type=content_type,
        host_address=host_address,
        phases=phases,
    )


async def probe_stream(cfg: Config) -> AsyncIterator[ProbeResult]:
    # Check if this is a TCP probe
    parsed_url = urlparse(cfg.url)
    is_tcp = parsed_url.scheme == "tcp"

    if is_tcp:
        # Handle TCP probing
        hostname = parsed_url.hostname
        port = parsed_url.port

        if not hostname:
            # Return error result for invalid TCP URL
            error_result = ProbeResult(
                ts=time.time(),
                seq=1,
                latency_ms=0.0,
                status_code=None,
                error="InvalidTCPURL:NoHostname",
                bytes_read=0,
                content_type=None,
                host_address=None,
            )
            yield error_result
            return

        if not port:
            # Return error result for missing port
            error_result = ProbeResult(
                ts=time.time(),
                seq=1,
                latency_ms=0.0,
                status_code=None,
                error="InvalidTCPURL:NoPort",
                bytes_read=0,
                content_type=None,
                host_address=None,
            )
            yield error_result
            return

        # Handle DNS resolution once for TCP
        resolved_ip = None
        if cfg.resolve_once:
            try:
                resolved_ip, _, dns_error = await resolve_hostname_with_timing(
                    hostname, cfg
                )
                if dns_error:
                    resolved_ip = None
            except Exception:
                resolved_ip = None

        # TCP probing loop
        seq = 0
        start_time = time.monotonic()
        while True:
            seq += 1
            scheduled_next = start_time + seq * cfg.interval
            res = await probe_tcp_once(cfg, seq, hostname, port, resolved_ip)
            yield res
            if cfg.count and seq >= cfg.count:
                break
            # drift correction
            now = time.monotonic()
            sleep_for = scheduled_next - now
            if sleep_for > 0:
                try:
                    await asyncio.sleep(sleep_for)
                except asyncio.CancelledError:
                    break
        return

    # Original HTTP probing logic
    timeout = httpx.Timeout(cfg.timeout)

    # Build client configuration
    client_kwargs: dict[str, Any] = {
        "timeout": timeout,
    }

    # Handle keep-alive setting
    if not cfg.keepalive:
        client_kwargs["limits"] = httpx.Limits(max_keepalive_connections=0)

    # Handle TLS verification
    if cfg.insecure:
        client_kwargs["verify"] = False

    # Handle authentication
    auth = None
    if cfg.auth:
        if cfg.auth.startswith("bearer:"):
            # Bearer token auth
            token = cfg.auth[7:]  # Remove 'bearer:' prefix
            client_kwargs["headers"] = {"Authorization": f"Bearer {token}"}
        elif ":" in cfg.auth:
            # Basic auth
            user, password = cfg.auth.split(":", 1)
            auth = (user, password)

    if auth:
        client_kwargs["auth"] = auth

    # Set custom user agent
    headers: dict[str, str] = client_kwargs.get("headers", {})
    if cfg.user_agent:
        headers["User-Agent"] = cfg.user_agent
    if headers:
        client_kwargs["headers"] = headers

    # Handle DNS resolution once
    resolved_ip = None
    if cfg.resolve_once:
        try:
            parsed_url = urlparse(cfg.url)
            hostname = parsed_url.hostname
            if hostname:
                resolved_ip, _, dns_error = await resolve_hostname_with_timing(
                    hostname, cfg
                )
                if dns_error:
                    # If DNS resolution fails, we'll let individual probes handle it
                    resolved_ip = None
                if resolved_ip:
                    # Replace hostname with IP in URL for subsequent requests
                    modified_url = cfg.url.replace(hostname, resolved_ip, 1)
                else:
                    modified_url = cfg.url
            else:
                modified_url = cfg.url
        except Exception:
            modified_url = cfg.url
    else:
        modified_url = cfg.url

    async with httpx.AsyncClient(**client_kwargs) as client:
        seq = 0
        start_time = time.monotonic()
        while True:
            seq += 1
            scheduled_next = start_time + seq * cfg.interval
            res = await probe_once(client, cfg, seq, modified_url, resolved_ip)
            yield res
            if cfg.count and seq >= cfg.count:
                break
            # drift correction
            now = time.monotonic()
            sleep_for = scheduled_next - now
            if sleep_for > 0:
                try:
                    await asyncio.sleep(sleep_for)
                except asyncio.CancelledError:
                    break
