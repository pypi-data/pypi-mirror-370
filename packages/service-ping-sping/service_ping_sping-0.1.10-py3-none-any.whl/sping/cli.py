"""CLI interface for sping."""

import asyncio
import time
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.measure import Measurement
from rich.panel import Panel
from rich.segment import Segment
from rich.style import Style
from rich.table import Table

from . import __version__
from .config import Config
from .metrics import Metrics
from .probe import probe_stream


class BarChart:
    """Custom renderable for bar chart that controls exact line width."""

    def __init__(self, values, width: int, height: int):
        self.values = values
        self.width = width
        self.height = height

    def __rich_console__(self, console, options):
        # Force exact width regardless of content
        max_width = min(self.width, options.max_width or self.width)

        if max_width < 12:
            # Fallback for very narrow
            for _ in range(self.height):
                yield Segment(" " * max_width)
            return

        AXIS_W = 6
        SEP = " │"  # 2 chars
        plot_w = max(1, max_width - AXIS_W - len(SEP))

        if not self.values:
            empty_bar = " " * plot_w
            for _ in range(self.height):
                line = f"{'':>{AXIS_W}}{SEP}{empty_bar}"
                yield Segment(line[:max_width])
            return

        subset = self.values[-plot_w:] if len(self.values) > plot_w else self.values
        if not subset:
            empty_bar = " " * plot_w
            for _ in range(self.height):
                line = f"{'':>{AXIS_W}}{SEP}{empty_bar}"
                yield Segment(line[:max_width])
            return

        vmin, vmax = min(subset), max(subset)

        # Improve y-scale for startup: use 0 as minimum when we have limited data
        # This provides better range initialization and prevents scale issues
        if len(subset) <= 2:
            vmin = 0.0  # Use 0 as minimum for better initial scaling

        span = vmax - vmin

        if span < 1e-9:  # flat values
            bar_chars = "█" * len(subset)
            padded_bar = bar_chars.ljust(plot_w)
            label_text = f"{vmax:.1f}"[:AXIS_W].rjust(AXIS_W)

            for i in range(self.height):
                if i == self.height - 1:
                    # Bottom row with label and gradient bars
                    # For flat values, use medium purple since they're all the same
                    label_color = self._color_for_latency_value(vmax, vmax, vmax)
                    segments = [Segment(f"{label_text}{SEP}", Style(color=label_color))]

                    # Use value-based color for flat values
                    bar_color = self._color_for_latency_value(vmax, vmax, vmax)
                    segments.append(Segment(bar_chars, Style(color=bar_color)))
                    segments.append(Segment(" " * (plot_w - len(bar_chars)), Style()))

                    for seg in segments:
                        yield seg
                    yield Segment.line()
                else:
                    line = f"{'':>{AXIS_W}}{SEP}{padded_bar}"
                    yield Segment(line[:max_width])
                    yield Segment.line()
            return

        # Scale values to heights
        scaled = []
        for v in subset:
            h = max(1, int((v - vmin) / span * (self.height - 1)) + 1)
            scaled.append(h)

        # Build grid
        grid = [[" "] * plot_w for _ in range(self.height)]

        # Improved positioning: fill left-to-right until full, then scroll right
        # This provides intuitive startup behavior and smooth transition to scrolling
        if len(subset) < plot_w:
            start_x = 0  # Left-align when chart is not full (filling phase)
        else:
            start_x = (
                0  # When full, subset is already the rightmost data (scrolling phase)
            )

        for idx, (val, h) in enumerate(zip(subset, scaled)):
            x = start_x + idx
            if 0 <= x < plot_w:
                for y in range(self.height - h, self.height):
                    if 0 <= y < self.height:
                        # Height-based gradient: each bar shows gradient from its bottom to top
                        # y represents the row (0 = top of chart, height-1 = bottom of chart)
                        # For this bar, bottom is at (height - 1), top is at (height - h)

                        bar_bottom = self.height - 1
                        bar_height = h

                        # Position within this specific bar (0.0 = bottom of bar, 1.0 = top of bar)
                        bar_position = (
                            (bar_bottom - y) / (bar_height - 1)
                            if bar_height > 1
                            else 0.0
                        )

                        # Map bar position to gradient based on the bar's height
                        # Short bars only use lower colors, tall bars use full range
                        max_gradient_position = (
                            h / self.height
                        )  # How much of full gradient this bar uses
                        gradient_position = bar_position * max_gradient_position

                        # Apply the gradient position to our color scheme
                        if gradient_position <= 0.1:
                            color = "grey39"  # Very low - dark greyish blue
                        elif gradient_position <= 0.2:
                            color = "grey50"
                        elif gradient_position <= 0.3:
                            color = "slate_blue3"  # Low - moving toward purple
                        elif gradient_position <= 0.4:
                            color = "slate_blue1"
                        elif gradient_position <= 0.5:
                            color = "medium_purple3"  # Medium-low - dusty purple range
                        elif gradient_position <= 0.6:
                            color = "medium_purple1"
                        elif gradient_position <= 0.7:
                            color = "plum3"  # Medium-high - toward pink
                        elif gradient_position <= 0.8:
                            color = "plum1"
                        elif gradient_position <= 0.9:
                            color = "light_pink3"  # High - dusty pink range
                        else:
                            color = "light_pink1"  # Very high - bright dusty pink

                        grid[y][x] = (color, "█")

        # Generate output with colored labels
        mid_val = (vmin + vmax) / 2.0
        for i in range(self.height):
            # Determine label and its color
            if i == 0:
                label_val = vmax
                label_text = f"{vmax:.1f}"[:AXIS_W].rjust(AXIS_W)
            elif i == self.height - 1:
                label_val = vmin
                label_text = f"{vmin:.1f}"[:AXIS_W].rjust(AXIS_W)
            elif i == self.height // 2:
                label_val = mid_val
                label_text = f"{mid_val:.1f}"[:AXIS_W].rjust(AXIS_W)
            else:
                label_val = None
                label_text = "".rjust(AXIS_W)

            # Color the label based on its value
            if label_val is not None:
                label_color = self._color_for_latency_value(label_val, vmin, vmax)
                yield Segment(f"{label_text}{SEP}", Style(color=label_color))
            else:
                yield Segment(f"{label_text}{SEP}", Style())

            # Output bar segments with colors
            for x in range(plot_w):
                if x < len(grid[i]) and isinstance(grid[i][x], tuple):
                    color, char = grid[i][x]
                    yield Segment(char, Style(color=color))
                else:
                    yield Segment(" ", Style())

            yield Segment.line()

    def __rich_measure__(self, console, options):
        return Measurement(self.width, self.width)

    def _color_for_height_position(self, y_position, total_height):
        """Get color based on absolute position in the container (fixed gradient)."""
        # y_position: 0 = bottom of container, total_height-1 = top of container
        # Fixed gradient from blue (bottom) to green (top) across the entire container

        height_ratio = y_position / (total_height - 1) if total_height > 1 else 0.0

        if height_ratio <= 0.15:
            return "slate_blue1"  # Very bottom - gray-blue
        elif height_ratio <= 0.30:
            return "blue"  # Low - standard blue
        elif height_ratio <= 0.45:
            return "dodger_blue1"  # Lower middle - brighter blue
        elif height_ratio <= 0.60:
            return "deep_sky_blue1"  # Middle - sky blue
        elif height_ratio <= 0.75:
            return "cyan"  # Upper middle - cyan
        elif height_ratio <= 0.90:
            return "spring_green1"  # High - spring green
        else:
            return "bright_green"  # Top - bright neon green

    def _color_for_latency_value(self, value, min_val, max_val):
        """Get color based on latency value (dark greyish blue -> dusty purple -> dusty pink)."""
        if max_val <= min_val:
            return "grey50"  # Fallback for flat data

        # Calculate position in range (0.0 = min, 1.0 = max)
        position = (value - min_val) / (max_val - min_val)

        # Enhanced gradient: dark greyish blue -> dusty purple -> dusty pink
        if position <= 0.1:
            return "grey39"  # Very low - dark greyish blue
        elif position <= 0.2:
            return "grey50"
        elif position <= 0.3:
            return "slate_blue3"  # Low - moving toward purple
        elif position <= 0.4:
            return "slate_blue1"
        elif position <= 0.5:
            return "medium_purple3"  # Medium-low - dusty purple range
        elif position <= 0.6:
            return "medium_purple1"
        elif position <= 0.7:
            return "plum3"  # Medium-high - toward pink
        elif position <= 0.8:
            return "plum1"
        elif position <= 0.9:
            return "light_pink3"  # High - dusty pink range
        else:
            return "light_pink1"  # Very high - bright dusty pink


async def run(cfg: Config):
    """Main runner for sping."""
    console = Console()
    metrics = Metrics()

    # Track threshold violations for exit codes
    warn_violations = 0
    crit_violations = 0

    # Setup file export if requested
    export_file_handle = None
    if cfg.export_file:
        try:
            export_file_handle = open(cfg.export_file, "a")
        except Exception as e:
            console.print(
                f"[red]Warning: Could not open export file {cfg.export_file}: {e}[/]"
            )

    async def handle_result(r):
        nonlocal warn_violations, crit_violations

        metrics.update(r)

        # Check thresholds for successful probes
        if r.error is None:
            if cfg.crit_threshold and r.latency_ms > cfg.crit_threshold:
                crit_violations += 1
            elif cfg.warn_threshold and r.latency_ms > cfg.warn_threshold:
                warn_violations += 1

        # Export to file if configured
        if export_file_handle:
            try:
                import json as json_module

                export_file_handle.write(json_module.dumps(r.to_dict()) + "\n")
                export_file_handle.flush()
            except Exception:
                pass  # Fail silently for export errors

        if cfg.mode == "json":
            import json as json_module

            probe_data = {
                "seq": r.seq,
                "timestamp": r.ts,
                "latency_ms": r.latency_ms,
                "status_code": r.status_code,
                "error": r.error,
                "bytes_read": r.bytes_read,
                "content_type": r.content_type,
                "host_address": r.host_address,
                "anomaly": getattr(r, "anomaly", False),
            }
            # Add phase information if available
            if r.phases:
                probe_data["phases"] = {
                    "dns_ms": r.phases.dns,
                    "connect_ms": r.phases.connect,
                    "tls_ms": r.phases.tls,
                    "request_write_ms": r.phases.request_write,
                    "ttfb_ms": r.phases.ttfb,
                    "body_read_ms": r.phases.body_read,
                    "total_ms": r.phases.total,
                }
            print(json_module.dumps(probe_data))
        elif cfg.mode == "plain":
            if r.error:
                error_marker = " [ANOMALY]" if getattr(r, "anomaly", False) else ""
                print(f"[{r.seq}] {r.ts}: error: {r.error}{error_marker}")
            else:
                response_info = []
                if r.bytes_read > 0:
                    response_info.append(f"{r.bytes_read}B")
                if r.content_type:
                    response_info.append(r.content_type.split(";")[0])
                response_str = f" ({', '.join(response_info)})" if response_info else ""
                host_str = f" from {r.host_address}" if r.host_address else ""
                anomaly_marker = " [ANOMALY]" if getattr(r, "anomaly", False) else ""
                threshold_marker = ""
                if cfg.crit_threshold and r.latency_ms > cfg.crit_threshold:
                    threshold_marker = " [CRITICAL]"
                elif cfg.warn_threshold and r.latency_ms > cfg.warn_threshold:
                    threshold_marker = " [WARNING]"

                # Format status for TCP vs HTTP
                if r.content_type == "tcp/connection":
                    # TCP connection result
                    status_str = "connected" if r.status_code == 0 else "failed"
                else:
                    # HTTP result
                    status_str = str(r.status_code) if r.status_code else "error"

                print(
                    f"[{r.seq}] {r.ts}: {r.latency_ms:.3f}ms {status_str}{response_str}{host_str}{anomaly_marker}{threshold_marker}"
                )

    results_aiter = probe_stream(cfg)

    try:
        if cfg.mode != "interactive":
            async for r in results_aiter:
                await handle_result(r)
            # summary
            s = metrics.summary()
            summary_lines = [
                f"--- {cfg.url} sping summary ---",
                f"{s['count']} probes, {s['ok']} ok, {s['errors']} errors",
            ]

            if s.get("anomalies", 0) > 0:
                summary_lines.append(f"Anomalies detected: {s['anomalies']}")

            latency_line = f"Latency (ms): min {s['min']:.3f} mean {s['mean']:.3f} max {s['max']:.3f}"
            if cfg.show_percentiles and s.get("p50") is not None:
                latency_line += f" p50 {s['p50']:.3f} p90 {s['p90']:.3f} p95 {s['p95']:.3f} p99 {s['p99']:.3f}"
            summary_lines.append(latency_line)

            if s["count"] > 1:
                summary_lines.append(f"Standard deviation: {s.get('stdev', 0):.3f}ms")

            if warn_violations > 0 or crit_violations > 0:
                summary_lines.append(
                    f"Threshold violations: {warn_violations} warnings, {crit_violations} critical"
                )

            console.print("\n".join(summary_lines))

            # Determine exit code
            if crit_violations > 0:
                return 2  # Critical threshold exceeded
            elif warn_violations > 0:
                return 1  # Warning threshold exceeded
            return 0

        # interactive mode continues as before but with anomaly detection...
        def compute_top_height() -> int:
            # Reserve ~40% of vertical real estate within bounds
            term_h = console.size.height
            # subtract panel borders & summary lines (approx 6)
            usable = max(5, term_h - 6)
            target = int(usable * 0.4)
            return max(5, min(target, 15))

        def render_panel():
            # Determine width
            width = console.size.width - 4
            if width < 20:
                width = 20
            # Data
            latencies = metrics.last_latencies(width)
            top_height = compute_top_height()

            # Don't start drawing the bar graph until we have at least one poll result
            # This prevents y-scale rendering issues and incorrect bar positioning at startup
            if not latencies:
                # Show empty chart while waiting for first result
                chart = BarChart([], width - 2, top_height)  # -2 for panel padding
            else:
                chart = BarChart(
                    latencies, width - 2, top_height
                )  # -2 for panel padding

            # Calculate time span for the chart
            chart_title = f"sping {cfg.url}"
            if len(latencies) > 1:
                # Get the time span of the data shown in the chart
                time_span_seconds = len(latencies)  # Each bar represents 1 second
                if time_span_seconds >= 60:
                    time_span_minutes = time_span_seconds / 60
                    chart_title += f" (last {time_span_minutes:.1f}m)"
                else:
                    chart_title += f" (last {time_span_seconds}s)"

            stats = metrics.summary()
            stat_text = (
                f"count {stats['count']} [deep_sky_blue1]ok {stats['ok']}[/] [orange_red1]err {stats['errors']}[/] "
                f"min {stats['min']:.1f} [medium_purple1]mean {stats['mean']:.1f}[/] max {stats['max']:.1f}"
                if stats["count"] > 0
                else "(waiting for samples)"
            )
            if stats.get("anomalies", 0) > 0:
                stat_text += f" [red]anomalies {stats['anomalies']}[/]"

            top_content = chart
            # Log panel - fixed height with padding for empty rows
            log_panel = Table(box=None, expand=True, show_header=True)
            log_panel.add_column("Seq", justify="left", width=4)
            log_panel.add_column("Time", width=8)
            log_panel.add_column("Host", width=25)
            log_panel.add_column("Response")
            log_panel.add_column("Latency", justify="right", width=8)

            # Get events and pad to always show 10 rows
            events = metrics.tail_events(10)

            # Get full event history for accurate IP change detection
            all_events = list(metrics.events)

            # Calculate min/max latency for consistent coloring (excluding errors)
            valid_latencies = [e.latency_ms for e in events if e.error is None]
            if valid_latencies:
                min_latency = min(valid_latencies)
                max_latency = max(valid_latencies)
            else:
                min_latency = max_latency = 0.0

            # Helper function for consistent latency coloring
            def get_latency_color_for_log(value):
                if max_latency <= min_latency:
                    return "grey50"  # Fallback for flat data

                # Calculate position in range (0.0 = min, 1.0 = max)
                position = (value - min_latency) / (max_latency - min_latency)

                # Enhanced gradient: dark greyish blue -> dusty purple -> dusty pink
                if position <= 0.1:
                    return "grey39"  # Very low - dark greyish blue
                elif position <= 0.2:
                    return "grey50"
                elif position <= 0.3:
                    return "slate_blue3"  # Low - moving toward purple
                elif position <= 0.4:
                    return "slate_blue1"
                elif position <= 0.5:
                    return "medium_purple3"  # Medium-low - dusty purple range
                elif position <= 0.6:
                    return "medium_purple1"
                elif position <= 0.7:
                    return "plum3"  # Medium-high - toward pink
                elif position <= 0.8:
                    return "plum1"
                elif position <= 0.9:
                    return "light_pink3"  # High - dusty pink range
                else:
                    return "light_pink1"  # Very high - bright dusty pink

            for i in range(10):
                if i < len(events):
                    row = events[i]

                    # Format time (HH:MM:SS)
                    import datetime

                    time_str = f"[grey50]{datetime.datetime.fromtimestamp(row.ts).strftime('%H:%M:%S')}[/]"

                    # Host address - highlight IP in pink if it changed from previous
                    host_str = ""
                    if row.host_address:
                        # Find this event in the full history to get accurate previous event
                        prev_ip = None
                        if len(all_events) > 1:
                            # Find the index of current event in full history
                            current_event_idx = None
                            for idx, event in enumerate(all_events):
                                if (
                                    event.ts == row.ts
                                    and event.host_address == row.host_address
                                    and event.latency_ms == row.latency_ms
                                ):
                                    current_event_idx = idx
                                    break

                            # Look for previous event with host_address
                            if current_event_idx is not None and current_event_idx > 0:
                                for j in range(current_event_idx - 1, -1, -1):
                                    if all_events[j].host_address:
                                        prev_ip = all_events[j].host_address
                                        break

                        # Extract hostname and IP from host_address (format: "hostname (ip)")
                        if " (" in row.host_address and row.host_address.endswith(")"):
                            hostname, ip_part = row.host_address.split(" (", 1)
                            ip = ip_part.rstrip(")")

                            # Check if IP changed
                            if prev_ip and prev_ip != row.host_address:
                                # Extract previous IP for comparison
                                if " (" in prev_ip and prev_ip.endswith(")"):
                                    prev_ip_only = prev_ip.split(" (", 1)[1].rstrip(")")
                                    if ip != prev_ip_only:
                                        # IP changed - highlight in pink
                                        host_str = (
                                            f"{hostname} ([bright_magenta]{ip}[/])"
                                        )
                                    else:
                                        host_str = row.host_address
                                else:
                                    # Previous format different, assume change
                                    host_str = f"{hostname} ([bright_magenta]{ip}[/])"
                            else:
                                host_str = row.host_address
                        else:
                            host_str = row.host_address

                    # Response info
                    if row.error:
                        # Show error in orange/red
                        response_info = f"[orange_red1]{row.error}[/]"
                    else:
                        # Build response info: status code (blue) + bytes + content-type
                        response_parts = []

                        # Status - handle TCP vs HTTP differently
                        if row.content_type == "tcp/connection":
                            # TCP connection result
                            if row.status_code == 0:
                                response_parts.append("[deep_sky_blue1]connected[/]")
                            else:
                                response_parts.append("[orange_red1]failed[/]")
                        else:
                            # HTTP status code in deep blue
                            if row.status_code:
                                response_parts.append(
                                    f"[deep_sky_blue1]{row.status_code}[/]"
                                )

                        # Bytes
                        if row.bytes_read > 0:
                            if row.bytes_read >= 1024:
                                response_parts.append(f"{row.bytes_read/1024:.1f}KB")
                            else:
                                response_parts.append(f"{row.bytes_read}B")

                        # Content type
                        if row.content_type:
                            # Shorten common content types
                            ct = row.content_type
                            if ct == "tcp/connection":
                                response_parts.append("tcp")
                            elif "text/html" in ct:
                                response_parts.append("html")
                            elif "application/json" in ct:
                                response_parts.append("json")
                            elif "text/plain" in ct:
                                response_parts.append("text")
                            elif "image/" in ct:
                                response_parts.append("image")
                            else:
                                # Take first part before semicolon and show last segment
                                ct_clean = ct.split(";")[0]
                                if "/" in ct_clean:
                                    response_parts.append(ct_clean.split("/")[-1])
                                else:
                                    response_parts.append(ct_clean)

                        response_info = (
                            " ".join(response_parts) if response_parts else ""
                        )

                    # Latency with consistent range-based purple coloring
                    latency_str = ""
                    if row.error is None:
                        # Use consistent range-based coloring
                        latency_color = get_latency_color_for_log(row.latency_ms)
                        latency_str = f"[{latency_color}]{row.latency_ms:.1f}ms[/]"

                    log_panel.add_row(
                        f"[dim blue]{row.seq}[/]",
                        time_str,
                        host_str,
                        response_info,
                        latency_str,
                        style="green" if not row.error else None,
                    )
                else:
                    # Add empty row to maintain fixed height of exactly 10 rows
                    log_panel.add_row("", "", "", "", "")

            # Calculate log panel height: header + 10 rows + padding
            log_height = 12  # header (1) + 10 rows + panel borders

            layout = Table.grid(expand=True)
            layout.add_row(
                Panel(
                    top_content,
                    title=chart_title,
                    height=top_height + 2,
                    padding=(0, 0),
                )
            )
            layout.add_row(Panel(log_panel, title=stat_text, height=log_height))
            return layout

        # Anti-flicker: Use configurable refresh rate and throttle updates
        refresh_rate = max(1.0, min(cfg.refresh_rate, 16.0))  # Clamp between 1-16 Hz

        with Live(console=console, refresh_per_second=refresh_rate) as live:
            live.update(render_panel())

            stop = False
            last_dims = (console.size.width, console.size.height)
            last_update_time = 0.0
            update_throttle_ms = 100  # Minimum 100ms between updates

            def should_update() -> bool:
                """Throttle updates to prevent excessive redraws that cause flickering."""
                nonlocal last_update_time
                current_time = time.time() * 1000  # Convert to milliseconds
                if current_time - last_update_time >= update_throttle_ms:
                    last_update_time = current_time
                    return True
                return False

            async def resize_poller():
                nonlocal last_dims
                try:
                    while not stop:
                        # Reduced polling frequency to decrease flicker potential
                        await asyncio.sleep(0.5)  # Increased from 0.3s to 0.5s
                        dims = (console.size.width, console.size.height)
                        if dims != last_dims and should_update():
                            last_dims = dims
                            live.update(render_panel())
                except asyncio.CancelledError:
                    pass

            poller_task = asyncio.create_task(resize_poller())
            try:
                async for r in results_aiter:
                    await handle_result(r)
                    # Throttle updates to reduce flickering on slow terminals
                    if should_update():
                        live.update(render_panel())
                    if cfg.count and r.seq >= cfg.count:
                        break
            finally:
                stop = True
                poller_task.cancel()
                try:
                    await poller_task
                except Exception:
                    pass

        # Print summary after interactive session
        s = metrics.summary()
        console.print(
            f"--- {cfg.url} sping summary ---\n"
            f"{s['count']} probes, {s['ok']} ok, {s['errors']} errors\n"
            f"Latency (ms): min {s['min']:.3f} mean {s['mean']:.3f} max {s['max']:.3f}"
        )
        return 0

    finally:
        # Clean up file handle
        if export_file_handle:
            export_file_handle.close()


app = typer.Typer()


def version_callback(value: bool):
    """Callback for --version option."""
    if value:
        console = Console()
        console.print(f"sping version {__version__}")
        raise typer.Exit()


@app.command()
def main(
    url: str = typer.Argument(..., help="URL to probe"),
    interval: float = typer.Option(1.0, help="Interval between probes in seconds"),
    count: Optional[int] = typer.Option(None, help="Number of probes to send"),
    timeout: float = typer.Option(10.0, help="Request timeout in seconds"),
    method: str = typer.Option("HEAD", help="HTTP method to use"),
    json_output: bool = typer.Option(False, "--json", help="JSON output mode"),
    plain: bool = typer.Option(False, "--plain", help="Plain text output mode"),
    body: bool = typer.Option(False, "--body", help="Include full body transfer time"),
    no_keepalive: bool = typer.Option(
        False, "--no-keepalive", help="Disable persistent connections"
    ),
    resolve_once: bool = typer.Option(
        False, "--resolve-once", help="Resolve DNS only once"
    ),
    user_agent: Optional[str] = typer.Option(
        None, "--user-agent", help="Custom User-Agent string"
    ),
    auth: Optional[str] = typer.Option(
        None, "--auth", help="Authentication: user:pass or bearer:token"
    ),
    insecure: bool = typer.Option(False, "--insecure", help="Skip TLS verification"),
    warn: Optional[float] = typer.Option(
        None, "--warn", help="Warning threshold in ms"
    ),
    crit: Optional[float] = typer.Option(
        None, "--crit", help="Critical threshold in ms"
    ),
    export_file: Optional[str] = typer.Option(
        None, "--export-file", help="Export JSON results to file"
    ),
    percentiles: bool = typer.Option(
        False, "--percentiles", help="Show percentiles in summary"
    ),
    refresh_rate: float = typer.Option(
        4.0,
        "--refresh-rate",
        help="UI refresh rate in Hz (lower values reduce flickering)",
    ),
    ipv4: bool = typer.Option(False, "--ipv4", help="Force IPv4 only"),
    ipv6: bool = typer.Option(False, "--ipv6", help="Force IPv6 only"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version and exit"
    ),
) -> None:
    """Modern HTTP/TCP latency monitoring tool with terminal UI."""
    # Validate conflicting options
    if ipv4 and ipv6:
        console = Console()
        console.print("[red]Error: --ipv4 and --ipv6 cannot be used together[/]")
        raise typer.Exit(1)

    # Preprocess URL - add http:// if no scheme provided
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"http://{url}"
    elif parsed.scheme == "tcp":
        # Validate TCP URL format
        if not parsed.hostname or not parsed.port:
            console = Console()
            console.print(
                "[red]Error: TCP URLs must include both hostname and port (e.g., tcp://example.com:80)[/]"
            )
            raise typer.Exit(1)

    # Determine mode
    if json_output:
        mode = "json"
    elif plain:
        mode = "plain"
    else:
        mode = "interactive"

    cfg = Config(
        url=url,
        interval=interval,
        count=count,
        timeout=timeout,
        method=method.upper(),
        include_body=body,
        mode=mode,
        keepalive=not no_keepalive,
        resolve_once=resolve_once,
        user_agent=user_agent,
        auth=auth,
        insecure=insecure,
        warn_threshold=warn,
        crit_threshold=crit,
        export_file=export_file,
        show_percentiles=percentiles,
        ipv4_only=ipv4,
        ipv6_only=ipv6,
        refresh_rate=refresh_rate,
    )

    exit_code = asyncio.run(run(cfg))
    if exit_code:
        raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
