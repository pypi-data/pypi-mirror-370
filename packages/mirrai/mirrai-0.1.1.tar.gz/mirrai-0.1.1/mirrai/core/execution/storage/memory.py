from typing import Dict, List, Optional, Tuple

from mirrai.core.execution.exceptions import ExecutionNotFoundError
from mirrai.core.execution.models import ExecutionState, ExecutionStatus
from mirrai.core.execution.storage.base import ExecutionStore


class MemoryExecutionStore(ExecutionStore):
    """In-memory implementation of execution storage.

    This is useful for testing and development. Data is lost when the
    process exits.
    """

    def __init__(self):
        self._executions: Dict[str, ExecutionState] = {}

    async def save_execution(self, execution: ExecutionState) -> None:
        """Save a new execution to memory."""
        self._executions[execution.id] = execution

    async def update_execution(self, execution: ExecutionState) -> None:
        """Update an existing execution in memory."""
        if execution.id not in self._executions:
            raise ExecutionNotFoundError(execution.id)
        self._executions[execution.id] = execution

    async def get_execution(self, execution_id: str) -> ExecutionState:
        """Retrieve an execution by ID from memory."""
        execution = self._executions.get(execution_id)
        if not execution:
            raise ExecutionNotFoundError(execution_id)
        return execution

    async def list_executions(
        self,
        status: Optional[ExecutionStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[ExecutionState], int]:
        """List executions from memory with optional filtering."""
        all_executions = list(self._executions.values())

        if status:
            all_executions = [e for e in all_executions if e.status == status]

        all_executions.sort(key=lambda e: e.created_at, reverse=True)  # newest first

        total = len(all_executions)
        paginated = all_executions[offset : offset + limit]

        return paginated, total

    async def delete_execution(self, execution_id: str) -> None:
        """Delete an execution from memory."""
        if execution_id not in self._executions:
            raise ExecutionNotFoundError(execution_id)
        del self._executions[execution_id]
