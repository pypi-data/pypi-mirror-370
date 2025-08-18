"""Execution-related exceptions."""

from typing import Optional


class ExecutionError(Exception):
    """Base exception for execution-related errors."""

    pass


class ExecutionAlreadyRunningError(ExecutionError):
    """Raised when attempting to start an execution while another is running."""

    def __init__(self, active_execution_id: str):
        self.active_execution_id = active_execution_id
        super().__init__(f"Execution {active_execution_id} is already running")


class ExecutionNotFoundError(ExecutionError):
    """Raised when an execution cannot be found."""

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        super().__init__(f"Execution {execution_id} not found")


class ExecutionNotRunningError(ExecutionError):
    """Raised when attempting to cancel an execution that is not running."""

    def __init__(self, execution_id: str, status: Optional[str] = None):
        self.execution_id = execution_id
        self.status = status
        msg = f"Execution {execution_id} is not running"
        if status:
            msg += f" (status: {status})"
        super().__init__(msg)
