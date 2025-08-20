"""NTT AI Observability Exporter for Azure Monitor OpenTelemetry."""

from .telemetry import configure_telemetry
from .semantic_kernel_telemetry import configure_semantic_kernel_telemetry



# Public API
__all__ = [
    "configure_telemetry",
    "configure_semantic_kernel_telemetry",
]