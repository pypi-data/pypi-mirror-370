import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from mirrai.core.constants import DEFAULT_MAX_ITERATIONS, DEFAULT_MAX_TOKENS, DEFAULT_PROVIDER


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
    max_tokens: int = DEFAULT_MAX_TOKENS
    quiet: bool = False
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    model: Optional[str] = None  # If None, will use provider's default model
    provider: str = DEFAULT_PROVIDER  # Provider type (anthropic, openrouter, etc.)
    provider_config: Optional[Dict[str, Any]] = None  # Provider-specific config


# ExecutionState has been merged into AgentExecution
# The AgentExecution class now owns all state and execution logic
