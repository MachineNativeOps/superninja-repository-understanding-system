"""
Observability Module: Logging, tracing, metrics, and event schemas.

This package provides comprehensive observability capabilities including
structured logging, distributed tracing, metrics collection, and
event schema definitions.
"""

from .event_schema import EventSchemaDef, EventSchemaRegistry, EventType
from .logging import LogContext, Logger, LogLevel
from .metrics import Metric, MetricsCollector, MetricType, Timer
from .tracing import Span, SpanStatus, Trace, Tracer

__all__ = [
    # Logging
    "Logger",
    "LogLevel",
    "LogContext",
    # Tracing
    "Tracer",
    "Span",
    "Trace",
    "SpanStatus",
    # Metrics
    "MetricsCollector",
    "Metric",
    "MetricType",
    "Timer",
    # Event Schemas
    "EventSchemaDef",
    "EventSchemaRegistry",
    "EventType",
]
