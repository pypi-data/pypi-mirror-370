from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass
from typing import Deque, List

from .probe import ProbeResult


@dataclass
class _Running:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0  # variance accumulator
    min_v: float = float("inf")
    max_v: float = float("-inf")

    def update(self, x: float):
        self.count += 1
        if x < self.min_v:
            self.min_v = x
        if x > self.max_v:
            self.max_v = x
        delta = x - self.mean
        self.mean += delta / self.count
        delta2 = x - self.mean
        self.m2 += delta * delta2

    def summary(self):
        if self.count == 0:
            return {
                "count": 0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
                "stdev": 0.0,
            }
        var = self.m2 / self.count if self.count > 1 else 0.0
        return {
            "count": self.count,
            "mean": self.mean,
            "min": self.min_v,
            "max": self.max_v,
            "stdev": var**0.5,
        }


class Metrics:
    def __init__(self, window: int = 1000):
        self.running = _Running()
        self.events: Deque[ProbeResult] = deque(maxlen=window)

        # For anomaly detection
        self._baseline_window = 30  # Number of samples to establish baseline
        self._anomaly_threshold = 6.0  # MAD threshold multiplier

    def update(self, res: ProbeResult):
        # Mark anomaly before adding to metrics
        if res.error is None:
            res.anomaly = self._detect_anomaly(res.latency_ms)
            self.running.update(res.latency_ms)
        else:
            res.anomaly = False
        self.events.append(res)

    def _detect_anomaly(self, latency_ms: float) -> bool:
        """Detect if current latency is anomalous using MAD (Median Absolute Deviation)."""
        # Get recent successful latencies for baseline
        recent_latencies = [
            e.latency_ms
            for e in list(self.events)[-self._baseline_window :]
            if e.error is None
        ]

        # Need at least 10 samples to detect anomalies
        if len(recent_latencies) < 10:
            return False

        try:
            median = statistics.median(recent_latencies)
            mad = statistics.median([abs(x - median) for x in recent_latencies])

            # Avoid division by zero
            if mad < 1e-6:
                return False

            # Check if current latency is anomalous
            deviation = abs(latency_ms - median) / mad
            return deviation > self._anomaly_threshold
        except Exception:
            return False

    def summary(self):
        s = self.running.summary()
        errors = sum(1 for e in self.events if e.error is not None)
        anomalies = sum(1 for e in self.events if hasattr(e, "anomaly") and e.anomaly)
        ok = s["count"]

        # Calculate percentiles from successful probes
        latencies = [e.latency_ms for e in self.events if e.error is None]
        percentiles = {}

        if len(latencies) >= 2:
            try:
                percentiles = {
                    "p50": statistics.quantiles(latencies, n=2)[0],  # median
                    "p90": statistics.quantiles(latencies, n=10)[8],  # 90th percentile
                    "p95": statistics.quantiles(latencies, n=20)[18],  # 95th percentile
                    "p99": (
                        statistics.quantiles(latencies, n=100)[98]
                        if len(latencies) >= 100
                        else latencies[-1]
                    ),  # 99th percentile
                }
            except Exception:
                # Fallback for edge cases
                sorted_latencies = sorted(latencies)
                n = len(sorted_latencies)
                percentiles = {
                    "p50": sorted_latencies[n // 2],
                    "p90": (
                        sorted_latencies[int(n * 0.9)]
                        if n > 10
                        else sorted_latencies[-1]
                    ),
                    "p95": (
                        sorted_latencies[int(n * 0.95)]
                        if n > 20
                        else sorted_latencies[-1]
                    ),
                    "p99": (
                        sorted_latencies[int(n * 0.99)]
                        if n > 100
                        else sorted_latencies[-1]
                    ),
                }

        return {
            "count": len(self.events),
            "ok": ok,
            "errors": errors,
            "anomalies": anomalies,
            "min": s["min"],
            "mean": s["mean"],
            "max": s["max"],
            "stdev": s["stdev"],
            **percentiles,
        }

    def last_latencies(self, n: int) -> List[float]:
        vals = [e.latency_ms for e in self.events if e.error is None]
        return vals[-n:]

    def tail_events(self, n: int):
        # return last n events
        return list(self.events)[-n:]
