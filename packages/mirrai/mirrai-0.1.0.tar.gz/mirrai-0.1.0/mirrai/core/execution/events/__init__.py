"""Execution event system with type-safe handlers."""

from mirrai.core.execution.events.emitter import ExecutionEventEmitter
from mirrai.core.execution.events.types import (
    ErrorEvent,
    EventType,
    ExecutionEvent,
    IterationEvent,
    MessageEvent,
    StatusChangeEvent,
    ToolUseEvent,
)

__all__ = [
    "EventType",
    "ExecutionEvent",
    "MessageEvent",
    "ToolUseEvent",
    "StatusChangeEvent",
    "ErrorEvent",
    "IterationEvent",
    "ExecutionEventEmitter",
]
