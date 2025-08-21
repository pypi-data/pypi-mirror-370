sping (service-ping) — Design Document

## Vision
Create a modern, beautiful, terminal-first latency monitoring CLI for HTTP(S) services. Like `httping` + a live observability dashboard: a split-screen TUI showing a continuously scrolling latency bar/line view (animated, color‑coded) above a structured event log and real‑time analytics. Fast startup, low overhead, ergonomic CLI, exportable metrics, and extensibility for future protocols.

## Primary Use Cases
1. Interactive watch: Operator runs `sping https://api.example.com` while debugging incidents and visually tracks latency / errors.
2. Headless scripting: Use machine-readable or JSON/NDJSON output for CI/CD health gates.
3. Alerting aid: Pipe summary metrics to Prometheus or exit with thresholds for automation.
4. Comparative mode (future): Watch multiple endpoints side-by-side.

## Core Feature Parity & Inspiration from `httping`
`httping` capabilities informing scope (grouped):
- Target & request: URL argument, HEAD vs GET, custom method (future), persistent connections, optional full body timing, redirects toggle.
- Timing granularity: connect time vs TLS handshake vs request/response latency vs total (modeled after httping's connect/exchange split).
- Interval & count: configurable probe interval (-i), maximum probe count (-c) or duration.
- Output: human and machine-readable (plain times / -1 on error), summary statistics (min/max/avg, stdev), transfer speed (optional when GET).
- Protocol & network: IPv4/IPv6 selection, proxy support, timeout control, interface binding (if privileges allow), DNS resolve once.
- HTTP features: status code display, User-Agent override, Referer, cookies, basic auth / bearer token, follow/unfollow redirects.
- TLS: certificate fingerprint (SHA256), expiry, SNI, version & cipher.
- Error handling: count and classify errors (DNS, connect, TLS, timeout, HTTP status class).
- Alerting: audible ping (future via bell), colored latency thresholding.

## Differentiators / Added Value
- Rich real-time TUI (Textual / Rich) with:
  - Top pane: scrolling sparkline + stacked bar (latency phase breakdown) and rolling histogram window.
  - Adaptive coloring by thresholds (green < p50 baseline, yellow between p50–p95, red > p95 or error markers).
  - Live stats panel (current, min/avg/max, p50/p90/p95/p99, error %, moving EWMA, jitter).
  - Optional multi-target lanes (future).
- Bottom pane log: structured events (timestamp, outcome, code, latency phases, anomaly flags).
- Anomaly detection: simple Z-score on EWMA residual or MAD-based outlier; highlight spikes.
- Export channels: stdout (plain), JSON line mode, Prometheus text exposition on ephemeral local port (future), file append.
- Plugin hooks for custom sinks (webhook, InfluxDB, etc.).
- Graceful degradation: if no TTY → auto fallback to plain / JSON.
- Theming & accessibility (contrast, color-blind palette, unicode fallback, optional braille graphs off).

## Non-Goals (Initial Release)
- Load generation / concurrency benchmarking (e.g., wrk/hey). Only sequential latency sampling.
- Protocols beyond HTTP(S). (Future: gRPC, TCP, ICMP wrapper.)
- Full synthetic transaction scripting.

## High-Level Architecture
```
┌────────────────────────────────────────────────────────────────┐
│ CLI (Typer)                                                     │
├────────────────────────────────────────────────────────────────┤
│ Config Parsing & Mode Selection                                 │
├───────────────┬───────────────────────┬─────────────────────────┤
│ Probe Engine  │ Metrics Aggregator    │ UI Layer (Textual/Rich) │
│ (async tasks) │ (rolling windows,     │ (Panels, charts, log)   │
│               │ stats, anomalies)     │                         │
├───────────────┴───────────┬───────────┴───────────┬────────────┤
│ Exporters (stdout, JSON,  | Plugin Bus | Alerting / Thresholds │
│ future Prometheus)        |           | (beep, exit codes)     │
└───────────────────────────┴───────────┴────────────────────────┘
```

### Components
1. CLI / Entry (`sping/__main__.py`): argument parsing, config object assembly, logging setup, decides interactive vs headless.
2. Config Model (`config.py`): dataclass / pydantic model containing target URL(s), interval, timeouts, counts, thresholds, output mode, method, TLS opts.
3. Probe Engine (`probe.py`):
   - Async loop scheduling probe at fixed interval (wall clock) with drift correction.
   - Uses `httpx.AsyncClient` for persistent connections (keep-alive, HTTP/2 optional).
   - Measures phases with high-resolution timer (time.monotonic_ns). Phases: dns (if measured), connect, tls, request_write, first_byte, body_read, total.
   - Emits `ProbeResult` events (success/error classification) onto an asyncio Queue.
4. Metrics Aggregator (`metrics.py`):
   - Consumes results, updates rolling ring buffers (deque capped to window length), online statistics (Welford algorithm), histograms (HDRHistogram or manual buckets), EWMA for trend.
   - Computes percentiles (approx via `TDigest` optional future; initial: sorted copy of small buffer or `statistics.quantiles`).
   - Anomaly detection: compute deviation > k * MAD or Z-score threshold.
5. UI Layer (`ui/`):
   - Textual App with Layout: Top (ChartsPanel), Right (StatsPanel), Bottom (LogPanel). Responsive resizing.
   - Live charts: implement custom `LatencyChart` widget rendering last N samples as stacked bars (connect/tls/request/response) or fallback line sparkline if narrow.
   - Log Panel: virtualized scroll of last M events; highlight errors & anomalies.
   - Keybinds: q quit, p pause, e expand stats, h help, m mode switch (bar <-> line), r reset stats, s save snapshot (JSON summary).
6. Exporters (`exporters/`): base interface + implementations for plain stdout, JSONL, Prometheus (future), file.
7. Plugin System (`plugins/` future): simple entrypoint-based discovery or dynamic import path; each plugin registers sink or transform.
8. Alerting & Exit Codes: optional `--warn latency_ms` `--crit latency_ms` thresholds; exit code set after run (or immediate if `--fail-fast`).
9. Theming: central palette; environment variable / flag to choose preset; fallback to ASCII safe mode if `TERM` lacks color.

## Data Models
```python
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
    ts: float  # epoch seconds
    seq: int
    url: str
    status_code: Optional[int]
    error: Optional[str]
    phases: ProbePhases
    bytes_read: int
    verified_tls: Optional[bool]
    cert_expiry_days: Optional[int]
    anomaly: bool
```
All timings stored in milliseconds (float) with microsecond precision conversion. Internal high precision kept in ns until conversion.

## Concurrency & Scheduling
- Single asyncio event loop.
- One probe coroutine per target (initially 1) with `asyncio.sleep` drift-corrected: compute next scheduled time = start + n*interval.
- Timeout enforced per request via httpx timeout config; if over, classify `timeout` error.
- Backpressure: aggregator queue size bounded; if full, drop oldest (log a warning / metric) to keep UI responsive.

## Latency Statistics
- Rolling window: default 5 minutes or last 300 samples (configurable), whichever fits memory target.
- Stats tracked: count_success, count_error, min, max, mean (online), variance (Welford), jitter (abs diff successive total latencies mean), percentiles (p50, p90, p95, p99), error rate.
- Histograms: bucket cutoffs (e.g., 5,10,20,50,100,200,300,500,750,1000,1500,2000,5000 ms) + overflow.
- Trend: EWMA(alpha ~ 0.2) + derivative for direction arrow.

## Anomaly Detection (Initial)
- Maintain median and MAD of last N totals; anomaly if |x - median| > k * MAD (k default 6).
- Flag results; colored red and annotate in log; optional sound bell.

## CLI Flags (Initial Draft)
```
sping [options] <url>
  -i, --interval <seconds>         Probe interval (default 1.0)
  -c, --count <n>                  Stop after n probes
  -d, --duration <seconds>         Stop after total duration
  -X, --method <METHOD>            HTTP method (HEAD default; GET if --body)
      --body                       Include full body transfer time
      --no-keepalive               Disable persistent connection
      --resolve-once               Resolve DNS once (skip subsequent lookups)
      --timeout <seconds>          Request timeout (default 5s)
      --connect-timeout <seconds>  Connect phase timeout override
      --header "Name: Value"       Extra header(s)
      --user-agent <string>
      --auth user:pass | bearer:<token>
      --insecure                   Skip TLS verification
      --fingerprint                Show TLS fingerprint initially
      --proxy <url>
      --ipv4 | --ipv6              Force address family
      --json                       JSON line output (disables interactive TUI)
      --plain                      Plain times only (machine-readable)
      --export-file <path>         Append JSON results to file
      --warn <ms>                  Warn threshold
      --crit <ms>                  Critical threshold
      --percentiles                Print percentiles in summary (headless)
      --no-ui                      Force disable UI
      --theme <name>
      --log-level <level>
      --version
```
(Future: `--prometheus-port`, multiple URLs, `--diff p95>baseline+X%`, `--hist` output.)

## UI Behavior
- On start: header line with target, interval, method, resolved IP, TLS info.
- Top: chart updates every sample; maintains ~N visible points (width of pane). Bars stacked by phase (fallback single color if too narrow). Errors show as red X marker.
- Right (or overlay): live stats table, updating in place.
- Bottom: structured log lines; truncated to last M (e.g., 500). Press `L` to toggle full-screen log.
- Resize-friendly; on very narrow terminals fallback to minimal numeric ticker.

## Logging
- Use `structlog` or standard logging with JSON option. Internal debug logs distinguish from user-facing log pane.

## Error Classification
- DNS failure, connect refused, TLS handshake, timeout, HTTP error (status >=400) but still success ping vs logical error flagged separately.
- Each classification increments specific counters for summary.

## Summary Output (Headless Completion)
Example (plain):
```
--- https://api.example.com sping summary ---
300 probes, 298 ok, 2 errors (timeout:1, http5xx:1)
Latency (ms): min 42.3  mean 55.8  max 412.6  p50 51.4  p90 63.2  p95 70.1  p99 388.9
Jitter mean: 3.2 ms  Error rate: 0.67%
Anomalies flagged: 4
```
Exit codes: 0 ok, 1 warn threshold exceeded (any sample > warn), 2 crit threshold exceeded.

## Persistence / Export
- JSON lines: one `ProbeResult` per line, plus periodic `stats` snapshot every N seconds.
- File sink reopened on rotate (SIGHUP detection future).

## Performance Considerations
- Single target sequential requests: overhead should be near `httpx` + timing instrumentation (<1ms added ideally).
- Avoid large per-sample allocations: reuse prepared request; keep hist arrays small.
- Efficient drawing: batch redraw at interval or on new sample only; coalesce; Textual already throttles.

## Dependencies (Initial)
- `httpx` (async client, HTTP/2)
- `rich` + `textual` (TUI rendering)
- `typer` (CLI)
- `pydantic` (config validation) — optional; pure dataclass if dependency minimization needed.
- `click` comes via Typer.
- (Optional future) `tdigest` or `hdrhistogram` for percentiles.
- `structlog` (optional) for structured logging.

Dependency Strategy: keep core minimal; gate extras behind extras: `pip install sping[ui,hdr]`.

## Packaging & Distribution
- Project layout:
```
sping/
  __init__.py
  __main__.py
  cli.py
  config.py
  probe.py
  metrics.py
  exporters/
    __init__.py
    base.py
    stdout.py
    jsonl.py
  ui/
    __init__.py
    app.py
    charts.py
    log_panel.py
    stats_panel.py
  plugins/ (future)
  util/time.py
  util/tls.py

tests/
  test_config.py
  test_probe_timing.py
  test_metrics_stats.py

pyproject.toml
README.md
```
- Entry point: console_scripts `sping=sping.__main__:main`.

## Testing Strategy
- Unit tests: probe timing (mock transport), metrics aggregator (stat correctness), anomaly detection thresholds.
- Integration: live local `pytest-httpserver` or simple aiohttp test server to simulate latency & errors.
- UI snapshot (optional) minimal smoke: run a few iterations in headless mode and ensure no exceptions.
- Performance micro-benchmark: run 1000 probes against loopback and assert overhead < threshold.

## Accessibility & UX
- Provide `--no-color` and high-contrast theme.
- Use Unicode sparingly; degrade to ASCII. Provide braille sparkline optional.
- Avoid rapid flashing; highlight anomalies with subtle color shifts.

## Observability for sping Itself
- Internal debug metrics: queue depth, redraw time, probe scheduling drift.
- Hidden flag `--debug-metrics` to surface.

## Security Considerations
- Sanitizes log outputs (avoid dumping auth headers).
- Optional `--insecure` clearly marked; UI displays warning.
- Limit path traversal for export file; ensure mode 0600 for sensitive outputs.

## Failure & Edge Cases
- Network partition: consecutive timeouts— display streak count.
- Clock adjustments: rely on monotonic for durations; wall clock only for display.
- Very slow terminal (remote over SSH): allow `--ui-refresh <Hz>` to throttle.
- Extremely high latency spikes: clamp chart scale with adaptive max; indicate overflow markers.

## Roadmap (Phased)
Phase 1 (MVP): single URL, HEAD, interval/count, timing phases (connect/total), TUI charts (basic line), JSON/headless, summary stats.
Phase 2: Phase breakdown bars, anomaly detection, percentiles, thresholds/exit codes, TLS fingerprint/expiry.
Phase 3: Multiple URLs, exporters (Prometheus), plugin hooks, histograms, comparative view.
Phase 4: Additional protocols (gRPC, WebSocket ping), advanced anomaly ML plugin.

## Risks & Mitigations
- TUI flicker / performance: choose Textual (async) and minimal redraw content; profile early.
- Timing accuracy: rely on monotonic_ns wraps; ensure phases measured around httpx events (may need custom Transport for fine-grained). Mitigate by providing coarse times if deep hooks complex initially.
- Dependency bloat: extras mechanism; base install small.
- Complexity creep: enforce config boundaries; plugin architecture to avoid core growth.

## Open Questions
- Need fine-grained phase breakdown: may implement custom `httpx` Transport subclass to intercept DNS/connect/TLS (httpx currently exposes some events via hooks). If insufficient, fallback to total + TTFB initially.
- Histogram library choice: implement simple bucket first; evaluate need for HDR.
- Multi-target layout ergonomics: vertical stacking vs grid.

## Definition of Done (Phase 1)
- `sping <url>` runs interactively w/ chart + log.
- Accurately reports per-sample total latency and success/error.
- Supports interval, count, timeout, method HEAD/GET, JSON headless mode.
- Provides summary with min/avg/max and error counts.
- Clean exit, no resource leaks (verified via async client close).

---
This design will evolve; changes tracked via CHANGELOG and updates to this document.
