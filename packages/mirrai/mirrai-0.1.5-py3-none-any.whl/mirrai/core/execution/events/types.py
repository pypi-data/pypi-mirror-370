"""Event types and dataclasses for execution events."""

from dataclasses import dataclass
from enum import Enum

from mirrai.core.execution.models import ExecutionStatus, Message, ToolUse


class EventType(str, Enum):
    """Types of execution events."""

    ALL = "*"
    MESSAGE = "message"
    TOOL_USE = "tool_use"
    STATUS_CHANGE = "status_change"
    ERROR = "error"
    ITERATION = "iteration"


@dataclass
class ExecutionEvent:
    """Base class for execution events."""

    type: EventType
    execution_id: str


@dataclass
class MessageEvent(ExecutionEvent):
    """Event fired when a message is added."""

    message: Message

    def __init__(self, execution_id: str, message: Message):
        super().__init__(EventType.MESSAGE, execution_id)
        self.message = message


@dataclass
class ToolUseEvent(ExecutionEvent):
    """Event fired when a tool is used."""

    tool_use: ToolUse

    def __init__(self, execution_id: str, tool_use: ToolUse):
        super().__init__(EventType.TOOL_USE, execution_id)
        self.tool_use = tool_use


@dataclass
class StatusChangeEvent(ExecutionEvent):
    """Event fired when execution status changes."""

    old_status: ExecutionStatus
    new_status: ExecutionStatus

    def __init__(self, execution_id: str, old_status: ExecutionStatus, new_status: ExecutionStatus):
        super().__init__(EventType.STATUS_CHANGE, execution_id)
        self.old_status = old_status
        self.new_status = new_status


@dataclass
class ErrorEvent(ExecutionEvent):
    """Event fired when an error occurs."""

    error: str

    def __init__(self, execution_id: str, error: str):
        super().__init__(EventType.ERROR, execution_id)
        self.error = error


@dataclass
class IterationEvent(ExecutionEvent):
    """Event fired when iteration count changes."""

    current: int
    max_iterations: int

    def __init__(self, execution_id: str, current: int, max_iterations: int):
        super().__init__(EventType.ITERATION, execution_id)
        self.current = current
        self.max_iterations = max_iterations


__all__ = [
    "EventType",
    "ExecutionEvent",
    "MessageEvent",
    "ToolUseEvent",
    "StatusChangeEvent",
    "ErrorEvent",
    "IterationEvent",
]
