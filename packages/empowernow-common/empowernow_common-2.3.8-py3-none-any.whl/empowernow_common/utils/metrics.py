try:
    from prometheus_client import CollectorRegistry, Gauge, generate_latest
except ImportError:  # pragma: no cover – optional dep
    class _DummyGauge:  # type: ignore
        def __init__(self, name: str, desc: str, registry=None):
            self._name = name
            self._value = 0

        def set(self, v):
            self._value = v

        @property
        def name(self):
            return self._name

        @property
        def value(self):
            return self._value

    def _dummy_generate(reg):
        lines = []
        for g in _METRIC_CACHE.values():
            lines.append(f"# TYPE {g.name} gauge\n{g.name} {g.value}\n")
        return "".join(lines).encode()

    CollectorRegistry = object  # type: ignore
    Gauge = _DummyGauge  # type: ignore
    generate_latest = _dummy_generate  # type: ignore

from typing import Dict

_REGISTRY = CollectorRegistry()
_METRIC_CACHE: Dict[str, Gauge] = {}


def export_metrics(metrics_dict: Dict[str, int]) -> bytes:
    """Convert internal metrics_dict to Prometheus exposition format."""
    for key, value in metrics_dict.items():
        gauge = _METRIC_CACHE.get(key)
        if not gauge:
            gauge = Gauge(
                f"empowernow_{key}", f"EmpowerNow metric: {key}", registry=_REGISTRY
            )
            _METRIC_CACHE[key] = gauge
        gauge.set(value)
    return generate_latest(_REGISTRY)
