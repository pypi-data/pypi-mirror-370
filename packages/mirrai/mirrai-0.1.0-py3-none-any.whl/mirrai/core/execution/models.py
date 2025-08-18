"""Core models for execution management."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

DEFAULT_MODEL = "claude-sonnet-4-20250514"


class ExecutionStatus(str, Enum):
    """Status of an agent execution."""

    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Message(BaseModel):
    """A message in the agent conversation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ToolUse(BaseModel):
    """Record of a tool use action."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class ExecutionRequest(BaseModel):
    """Request to start an execution."""

    task: str
    window: Optional[str] = None
    system_prompt: Optional[str] = None
    max_tokens: int = 4096
    execute_actions: bool = True
    debug_mode: bool = False
    max_iterations: int = 50
    model: str = DEFAULT_MODEL


class ExecutionState(BaseModel):
    """Complete state of an execution."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: ExecutionRequest
    status: ExecutionStatus = ExecutionStatus.IDLE
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    messages: List[Message] = Field(default_factory=list)
    tool_uses: List[ToolUse] = Field(default_factory=list)
    current_iteration: int = 0
    max_iterations: int = 50

    def add_message(self, role: Literal["user", "assistant", "system"], content: str) -> Message:
        """Add a message to the execution history."""
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message

    def add_tool_use(self, action: str, details: Dict[str, Any]) -> ToolUse:
        """Add a tool use record."""
        tool_use = ToolUse(action=action, details=details)
        self.tool_uses.append(tool_use)
        return tool_use

    def set_status(self, status: ExecutionStatus) -> None:
        """Update execution status."""
        self.status = status

        if status == ExecutionStatus.RUNNING and self.started_at is None:
            self.started_at = datetime.now()
        elif status in (
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        ):
            if self.completed_at is None:
                self.completed_at = datetime.now()

    def set_error(self, error: str) -> None:
        """Set error and mark as failed."""
        self.error = error
        self.set_status(ExecutionStatus.FAILED)
