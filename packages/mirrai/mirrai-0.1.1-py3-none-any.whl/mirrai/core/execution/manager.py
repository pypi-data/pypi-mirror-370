"""Core execution manager for agent tasks."""

import asyncio
from typing import Dict, List, Optional, Tuple

from mirrai.core.client import client
from mirrai.core.execution.events import (
    ErrorEvent,
    ExecutionEventEmitter,
    IterationEvent,
    MessageEvent,
    StatusChangeEvent,
    ToolUseEvent,
)
from mirrai.core.execution.exceptions import (
    ExecutionAlreadyRunningError,
    ExecutionNotFoundError,
    ExecutionNotRunningError,
)
from mirrai.core.execution.models import (
    ExecutionRequest,
    ExecutionState,
    ExecutionStatus,
)
from mirrai.core.execution.storage import ExecutionStore, MemoryExecutionStore
from mirrai.core.logger import logger


class ExecutionManager:
    """Manages agent executions with persistence and event handling."""

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        store: Optional[ExecutionStore] = None,
    ):
        """Initialize execution manager.

        Args:
            anthropic_api_key: API key for Anthropic (optional, will use env var if not provided)
            store: Storage backend (defaults to MemoryExecutionStore)
        """
        if anthropic_api_key:
            client.set_api_key(anthropic_api_key)

        self.store = store or MemoryExecutionStore()
        self.events = ExecutionEventEmitter()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._current_execution_id: Optional[str] = None

    async def create_execution(self, request: ExecutionRequest) -> ExecutionState:
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

        execution = ExecutionState(request=request)
        execution.set_status(ExecutionStatus.STARTING)
        await self.store.save_execution(execution)
        self._current_execution_id = execution.id

        task = asyncio.create_task(self._run_execution(execution))
        self._running_tasks[execution.id] = task

        return execution

    async def get_execution(self, execution_id: str) -> ExecutionState:
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
    ) -> Tuple[List[ExecutionState], int]:
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

        old_status = execution.status
        execution.set_status(ExecutionStatus.CANCELLED)
        execution.error = "Execution cancelled by user"
        await self.store.update_execution(execution)

        await self.events.emit_async(
            StatusChangeEvent(execution_id, old_status, ExecutionStatus.CANCELLED)
        )
        await self.events.emit_async(ErrorEvent(execution_id, "Execution cancelled by user"))

        if self._current_execution_id == execution_id:
            self._current_execution_id = None

    async def _run_execution(self, execution: ExecutionState) -> None:
        try:
            from mirrai.core.agent.execution import AgentExecution

            old_status = execution.status
            execution.set_status(ExecutionStatus.RUNNING)

            user_message = execution.add_message("user", execution.request.task)
            await self.store.update_execution(execution)

            await self.events.emit_async(
                StatusChangeEvent(execution.id, old_status, ExecutionStatus.RUNNING)
            )
            await self.events.emit_async(MessageEvent(execution.id, user_message))

            agent_execution = AgentExecution(execution.request)

            async def forward_message(event: MessageEvent) -> None:
                message = execution.add_message(event.message.role, event.message.content)
                await self.store.update_execution(execution)
                await self.events.emit_async(MessageEvent(execution.id, message))

            async def forward_tool_use(event: ToolUseEvent) -> None:
                tool_use = execution.add_tool_use(event.tool_use.action, event.tool_use.details)
                await self.store.update_execution(execution)
                await self.events.emit_async(ToolUseEvent(execution.id, tool_use))

            async def forward_iteration(event: IterationEvent) -> None:
                execution.current_iteration = event.current
                execution.max_iterations = event.max_iterations
                await self.store.update_execution(execution)
                await self.events.emit_async(
                    IterationEvent(execution.id, event.current, event.max_iterations)
                )

            agent_execution.events.messages.on_async(forward_message)
            agent_execution.events.tool_uses.on_async(forward_tool_use)
            agent_execution.events.iterations.on_async(forward_iteration)

            logger.info(f"Starting execution {execution.id}")
            await agent_execution.execute()

            old_status = execution.status
            execution.set_status(ExecutionStatus.COMPLETED)
            await self.store.update_execution(execution)

            await self.events.emit_async(
                StatusChangeEvent(execution.id, old_status, ExecutionStatus.COMPLETED)
            )

            logger.info(f"Execution {execution.id} completed successfully")

        except asyncio.CancelledError:
            # Already handled in cancel_execution
            raise

        except Exception as e:
            logger.error(f"Execution {execution.id} failed: {str(e)}")

            old_status = execution.status
            execution.set_error(str(e))
            await self.store.update_execution(execution)

            await self.events.emit_async(
                StatusChangeEvent(execution.id, old_status, ExecutionStatus.FAILED)
            )
            await self.events.emit_async(ErrorEvent(execution.id, str(e)))

        finally:
            if execution.id in self._running_tasks:
                del self._running_tasks[execution.id]

            if self._current_execution_id == execution.id:
                self._current_execution_id = None
