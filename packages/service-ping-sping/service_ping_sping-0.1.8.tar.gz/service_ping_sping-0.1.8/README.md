# service-ping (sping)

Modern terminal HTTP/TCP latency monitoring tool with real-time visualization. Think `httping` meets modern CLI design with rich terminal UI, phase timing, and advanced analytics.

**Status**: Feature-complete MVP with HTTP/TCP support, phase timing, anomaly detection, and comprehensive monitoring capabilities.

## Features

- 🌐 **HTTP & TCP Monitoring**: Support for `http://`, `https://`, and `tcp://` protocols
- 📊 **Real-time Visualization**: Interactive charts and live statistics in your terminal
- 🔍 **Phase Breakdown**: DNS, connection, TLS, request, and response timing
- 🚨 **Anomaly Detection**: Automatic outlier detection using MAD (Median Absolute Deviation)
- ⚠️ **Threshold Alerting**: Warning and critical thresholds with exit codes
- 🌍 **DNS Control**: IPv4/IPv6 selection and DNS resolution caching
- 📈 **Advanced Statistics**: Percentiles (p50, p90, p95, p99), standard deviation
- 💾 **Multiple Output Formats**: Interactive UI, plain text, JSON, and JSON export
- 🔐 **Authentication**: Bearer tokens and basic auth support
- 🎨 **Rich Terminal UI**: Beautiful charts, color-coded logs, and responsive layouts

## Demo

<img src="https://gitlab.com/dseltzer/sping/-/raw/master/demo/sping-graph-demo.gif" alt="sping Interactive Demo" width="50%">

*Real-time latency monitoring with interactive charts showing HTTP response times, anomaly detection, and live statistics.*

## Install

```bash
pip install service-ping-sping
```

For development:
```bash
pip install -e .[dev]
```

## Quick Start

```bash
# HTTP monitoring with interactive UI
sping google.com

# TCP connection monitoring
sping tcp://google.com:80

# HTTPS with custom options
sping https://api.example.com --interval 0.5 --count 20

# JSON output for automation
sping google.com --json --count 5

# Advanced monitoring with thresholds
sping example.com --warn 100 --crit 500 --percentiles
```

## Usage Examples

### HTTP/HTTPS Monitoring
```bash
# Basic HTTP monitoring (auto-adds http://)
sping example.com

# HTTPS with custom method and body transfer
sping https://api.example.com --method POST --body

# IPv4 only with DNS caching
sping google.com --ipv4 --resolve-once

# With authentication
sping api.example.com --auth "bearer:your-token"
sping api.example.com --auth "user:password"
```

### TCP Connection Monitoring
```bash
# Test TCP connectivity
sping tcp://google.com:80
sping tcp://example.com:443

# Monitor database connections
sping tcp://localhost:5432 --interval 0.1
```

### Advanced Features
```bash
# Anomaly detection and thresholds
sping example.com --warn 100 --crit 500 --count 100

# Export detailed timing data
sping example.com --export-file results.json --count 50

# Show percentile statistics
sping example.com --percentiles --count 100

# Plain output for scripting
sping example.com --plain --count 5
```

## Command Line Options

### Core Options
- `-i, --interval FLOAT`: Seconds between probes (default: 1.0)
- `-c, --count INT`: Number of probes then exit
- `--timeout FLOAT`: Request timeout in seconds (default: 10.0)
- `-X, --method TEXT`: HTTP method (default: HEAD)

### Protocol & DNS
- `--ipv4`: Force IPv4 only
- `--ipv6`: Force IPv6 only  
- `--resolve-once`: Resolve DNS only once and cache

### HTTP Options
- `--body`: Include full body transfer time
- `--no-keepalive`: Disable persistent connections
- `--user-agent TEXT`: Custom User-Agent string
- `--auth TEXT`: Authentication (user:pass or bearer:token)
- `--insecure`: Skip TLS verification

### Monitoring & Alerts
- `--warn FLOAT`: Warning threshold in milliseconds
- `--crit FLOAT`: Critical threshold in milliseconds
- `--percentiles`: Show percentile statistics in summary

### Output Formats
- `--json`: JSON output mode (one object per line)
- `--plain`: Plain text output mode
- `--export-file FILE`: Export JSON results to file

## Output Formats

### Interactive Mode (Default)
Real-time terminal UI with:
- Live latency chart with gradient coloring
- Recent requests log with timing details
- Statistics panel with min/mean/max/stdev
- Anomaly highlighting and threshold indicators

### Plain Text Mode (`--plain`)
```
[1] 1755658486.287: 484.313ms 200 (application/json) from httpbin.org (52.1.207.236)
--- https://httpbin.org/get sping summary ---
1 probes, 1 ok, 0 errors
Latency (ms): min 484.313 mean 484.313 max 484.313
```

### JSON Mode (`--json`)
```json
{"seq": 1, "timestamp": 1755658729.193, "latency_ms": 11.110, "status_code": 0, "error": null, "bytes_read": 0, "content_type": "tcp/connection", "host_address": "google.com (142.250.65.238)", "anomaly": false, "phases": {"dns_ms": 5.444, "connect_ms": 5.598, "tls_ms": null, "request_write_ms": null, "ttfb_ms": null, "body_read_ms": null, "total_ms": 11.110}}
```

## Phase Timing Breakdown

sping provides detailed timing for each phase of the connection:

- **DNS**: Domain name resolution time
- **Connect**: TCP connection establishment  
- **TLS**: TLS/SSL handshake time (HTTPS only)
- **Request Write**: Time to send HTTP request
- **TTFB**: Time to first byte (response headers)
- **Body Read**: Time to read response body
- **Total**: End-to-end request time

## Exit Codes

- `0`: Success
- `1`: Warning threshold exceeded (when `--warn` specified)
- `2`: Critical threshold exceeded (when `--crit` specified)

Perfect for monitoring scripts and alerting systems.

## Quit Interactive Mode

Press `Ctrl+C` to gracefully exit and see the final summary.

## Requirements

- Python 3.9+
- Modern terminal with color support recommended
- Works on Linux, macOS, and Windows

## License

MIT - see [LICENSE.md](LICENSE.md)
