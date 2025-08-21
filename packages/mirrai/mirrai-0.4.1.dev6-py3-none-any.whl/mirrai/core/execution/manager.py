import asyncio
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from mirrai.core.agent.execution import AgentExecution

from mirrai.core.execution.events import (
    IterationEvent,
    MessageEvent,
    ToolUseEvent,
)
from mirrai.core.execution.exceptions import (
    ExecutionAlreadyRunningError,
    ExecutionNotFoundError,
    ExecutionNotRunningError,
)
from mirrai.core.execution.models import (
    ExecutionRequest,
    ExecutionStatus,
)
from mirrai.core.execution.storage import ExecutionStore, MemoryExecutionStore
from mirrai.core.logger import logger


class ExecutionManager:
    """Manages agent executions with persistence and event handling."""

    def __init__(
        self,
        store: Optional[ExecutionStore] = None,
    ):
        """Initialize execution manager.

        Args:
            store: Storage backend (defaults to MemoryExecutionStore)
        """

        self.store = store or MemoryExecutionStore()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._current_execution_id: Optional[str] = None

    async def create_execution(self, request: ExecutionRequest) -> "AgentExecution":
        """Create and start a new execution.

        Args:
            request: Execution request parameters

        Returns:
            Created execution state

        Raises:
            ExecutionAlreadyRunningError: If another execution is already running
        """
        if self._current_execution_id:
            try:
                current = await self.store.get_execution(self._current_execution_id)
                if current.status == ExecutionStatus.RUNNING:
                    raise ExecutionAlreadyRunningError(self._current_execution_id)
            except ExecutionNotFoundError:
                # Current execution was deleted, can proceed
                self._current_execution_id = None

        from mirrai.core.agent.execution import AgentExecution

        agent_execution = AgentExecution(request)
        await agent_execution.set_status(ExecutionStatus.STARTING)
        await self.store.save_execution(agent_execution)
        self._current_execution_id = agent_execution.id

        task = asyncio.create_task(self._run_execution(agent_execution))
        self._running_tasks[agent_execution.id] = task

        return agent_execution

    async def get_execution(self, execution_id: str) -> "AgentExecution":
        """Get an execution by ID.

        Args:
            execution_id: Execution ID

        Returns:
            Execution state

        Raises:
            ExecutionNotFoundError: If execution doesn't exist
        """
        return await self.store.get_execution(execution_id)

    async def list_executions(
        self,
        status: Optional[ExecutionStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List["AgentExecution"], int]:
        """List executions with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum number to return
            offset: Pagination offset

        Returns:
            Tuple of (executions, total_count)
        """
        return await self.store.list_executions(status, limit, offset)

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running execution.

        Args:
            execution_id: Execution ID to cancel

        Raises:
            ExecutionNotFoundError: If execution doesn't exist
            ExecutionNotRunningError: If execution is not running
        """
        execution = await self.store.get_execution(execution_id)

        if execution.status != ExecutionStatus.RUNNING:
            raise ExecutionNotRunningError(execution_id, execution.status.value)

        if execution_id in self._running_tasks:
            task = self._running_tasks[execution_id]
            task.cancel()
            del self._running_tasks[execution_id]

        await execution.set_status(ExecutionStatus.CANCELLED)
        await execution.set_error("Execution cancelled by user")
        await self.store.update_execution(execution)

        if self._current_execution_id == execution_id:
            self._current_execution_id = None

    async def _run_execution(self, agent_execution) -> None:
        try:
            await agent_execution.set_status(ExecutionStatus.RUNNING)
            await self.store.update_execution(agent_execution)

            async def update_storage(event):
                logger.debug(
                    f"ExecutionManager: Received {type(event).__name__} from AgentExecution for storage update"
                )
                if isinstance(event, (MessageEvent, ToolUseEvent, IterationEvent)):
                    await self.store.update_execution(agent_execution)

            logger.debug(
                f"ExecutionManager: Subscribing to AgentExecution.events for storage updates only"
            )
            agent_execution.events.all.on_async(update_storage)

            logger.debug(f"ExecutionManager: Starting execution {agent_execution.id}")
            await agent_execution.execute()

            await agent_execution.set_status(ExecutionStatus.COMPLETED)
            await self.store.update_execution(agent_execution)

            logger.debug(f"Execution {agent_execution.id} completed successfully")

        except asyncio.CancelledError:
            # Already handled in cancel_execution
            raise

        except Exception as e:
            logger.error(f"Execution {agent_execution.id} failed: {str(e)}")

            await agent_execution.set_error(str(e))
            await self.store.update_execution(agent_execution)

        finally:
            if agent_execution.id in self._running_tasks:
                del self._running_tasks[agent_execution.id]

            if self._current_execution_id == agent_execution.id:
                self._current_execution_id = None
