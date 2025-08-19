from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass
class MetricsSnapshot:
    total_calls: int
    hits: int
    total_latency_ms: int
    cost_saved: float

    def to_dict(self) -> dict:
        avg_latency = (
            float(self.total_latency_ms) / self.total_calls if self.total_calls else 0.0
        )
        hit_rate = (
            (self.hits / self.total_calls) if self.total_calls else 0.0
        )
        return {
            "total_calls": self.total_calls,
            "hits": self.hits,
            "hit_rate": hit_rate,
            "avg_latency_ms": avg_latency,
            "cost_saved": self.cost_saved,
        }


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._total_calls = 0
        self._hits = 0
        self._total_latency_ms = 0
        self._cost_saved = 0.0

    def record_hit(self, latency_ms: int, cost_saved: float = 0.0) -> None:
        with self._lock:
            self._total_calls += 1
            self._hits += 1
            self._total_latency_ms += int(latency_ms)
            self._cost_saved += float(cost_saved)

    def record_miss(self, latency_ms: int) -> None:
        with self._lock:
            self._total_calls += 1
            self._total_latency_ms += int(latency_ms)

    def snapshot(self) -> MetricsSnapshot:
        with self._lock:
            return MetricsSnapshot(
                total_calls=self._total_calls,
                hits=self._hits,
                total_latency_ms=self._total_latency_ms,
                cost_saved=self._cost_saved,
            )

