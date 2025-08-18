from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from mirrai.core.execution.models import ExecutionState, ExecutionStatus


class ExecutionStore(ABC):
    """Abstract base class for execution storage backends."""

    @abstractmethod
    async def save_execution(self, execution: ExecutionState) -> None:
        """Save a new execution to storage.

        Args:
            execution: The execution state to save
        """
        pass

    @abstractmethod
    async def update_execution(self, execution: ExecutionState) -> None:
        """Update an existing execution in storage.

        Args:
            execution: The execution state to update

        Raises:
            ExecutionNotFoundError: If the execution doesn't exist
        """
        pass

    @abstractmethod
    async def get_execution(self, execution_id: str) -> ExecutionState:
        """Retrieve an execution by ID.

        Args:
            execution_id: The ID of the execution to retrieve

        Returns:
            The execution state

        Raises:
            ExecutionNotFoundError: If the execution doesn't exist
        """
        pass

    @abstractmethod
    async def list_executions(
        self,
        status: Optional[ExecutionStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[ExecutionState], int]:
        """List executions with optional filtering and pagination.

        Args:
            status: Optional status filter
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)

        Returns:
            Tuple of (executions, total_count)
        """
        pass

    @abstractmethod
    async def delete_execution(self, execution_id: str) -> None:
        """Delete an execution from storage.

        Args:
            execution_id: The ID of the execution to delete

        Raises:
            ExecutionNotFoundError: If the execution doesn't exist
        """
        pass
