from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from mirrai.core.execution.models import (
    ExecutionStatus,
    Message,
)
from mirrai.core.window_manager.models import Rect, WindowInfo


class WindowsResponse(BaseModel):
    """Response for listing windows."""

    windows: List[WindowInfo]


class WindowDetailResponse(BaseModel):
    """Detailed window information with additional fields."""

    window_info: WindowInfo
    client_rect: Optional[Rect] = None
    is_focused: bool = False


class FocusWindowResponse(BaseModel):
    """Response for focusing a window."""

    success: bool
    window_id: int


class CreateExecutionResponse(BaseModel):
    """Response for creating an execution."""

    execution_id: str
    status: ExecutionStatus
    created_at: datetime


class ExecutionResponse(BaseModel):
    """Full execution information including messages and timestamps."""

    execution_id: str
    status: ExecutionStatus
    created_at: datetime
    task: str
    window: Optional[str]
    messages: List[Message] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ExecutionListResponse(BaseModel):
    """Response for listing executions."""

    executions: List[ExecutionResponse]
    total: int
    limit: int
    offset: int


class SSEMessageType(str, Enum):
    """Types of SSE messages."""

    STATUS = "status"
    MESSAGE = "message"
    ACTION = "action"
    SCREENSHOT = "screenshot"
    COMPLETED = "completed"
    ERROR = "error"
    KEEPALIVE = "keepalive"


class SSEMessage(BaseModel):
    """Server-sent event message."""

    type: SSEMessageType
    data: Dict[str, Any]

    def to_sse_format(self) -> str:
        """Convert to SSE format string."""
        return f"data: {self.model_dump_json()}\n\n"


class SSEStatusData(BaseModel):
    """Data for status SSE messages."""

    status: ExecutionStatus


class SSEMessageData(BaseModel):
    """Data for message SSE messages."""

    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime


class SSEActionData(BaseModel):
    """Data for action SSE messages."""

    action: str  # e.g., "click", "type", "key", "screenshot"
    details: Dict[str, Any]  # e.g., {"x": 100, "y": 200} for click


class SSEErrorData(BaseModel):
    """Data for error SSE messages."""

    error: str
    details: Optional[str] = None
