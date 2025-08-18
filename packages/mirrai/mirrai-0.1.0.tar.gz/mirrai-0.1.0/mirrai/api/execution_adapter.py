import asyncio
from typing import AsyncGenerator, Optional

from mirrai.api.models import (
    SSEActionData,
    SSEErrorData,
    SSEMessage,
    SSEMessageData,
    SSEMessageType,
    SSEStatusData,
)
from mirrai.core.execution import ExecutionManager
from mirrai.core.execution.events import (
    ErrorEvent,
    ExecutionEvent,
    IterationEvent,
    MessageEvent,
    StatusChangeEvent,
    ToolUseEvent,
)
from mirrai.core.execution.exceptions import ExecutionNotFoundError
from mirrai.core.execution.models import ExecutionRequest, ExecutionState, ExecutionStatus


class APIExecutionManager:
    """Wraps core ExecutionManager with API-specific features like SSE."""

    def __init__(self, anthropic_api_key: str):
        """Initialize API execution manager.

        Args:
            anthropic_api_key: API key for Anthropic
        """
        self.core_manager = ExecutionManager(anthropic_api_key)
        self._sse_queue: Optional[asyncio.Queue[Optional[SSEMessage]]] = None
        self._current_execution_id: Optional[str] = None
        self.core_manager.events.all.on_async(self._handle_event_for_sse)

    async def create_execution(self, request: ExecutionRequest) -> ExecutionState:
        """Create and start a new execution.

        Args:
            request: Execution request parameters

        Returns:
            Created execution state
        """
        execution = await self.core_manager.create_execution(request)
        self._sse_queue = asyncio.Queue()
        self._current_execution_id = execution.id

        return execution

    async def get_execution(self, execution_id: str) -> ExecutionState:
        """Get an execution by ID."""
        return await self.core_manager.get_execution(execution_id)

    async def list_executions(
        self,
        status: Optional[ExecutionStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[ExecutionState], int]:
        """List executions with optional filtering."""
        return await self.core_manager.list_executions(status, limit, offset)

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running execution."""
        await self.core_manager.cancel_execution(execution_id)

    async def stream_execution(self, execution_id: str) -> AsyncGenerator[SSEMessage, None]:
        """Stream SSE events for an execution.

        Args:
            execution_id: Execution ID to stream

        Yields:
            SSE messages for the execution
        """
        try:
            execution = await self.get_execution(execution_id)
        except ExecutionNotFoundError:
            yield SSEMessage(type=SSEMessageType.ERROR, data={"error": "Execution not found"})
            return

        if execution_id != self._current_execution_id or not self._sse_queue:
            yield SSEMessage(type=SSEMessageType.ERROR, data={"error": "Not the current execution"})
            return

        queue = self._sse_queue

        yield SSEMessage(
            type=SSEMessageType.STATUS,
            data=SSEStatusData(status=execution.status).model_dump(),
        )

        if execution.status in (
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        ):
            yield SSEMessage(
                type=SSEMessageType.COMPLETED,
                data={"status": execution.status.value},
            )
            return

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                if event is None:
                    break

                yield event

            except asyncio.TimeoutError:
                yield SSEMessage(type=SSEMessageType.STATUS, data={"keepalive": True})  # keepalive

        if execution_id == self._current_execution_id:
            self._sse_queue = None
            self._current_execution_id = None

    async def _handle_event_for_sse(self, event: ExecutionEvent) -> None:
        """Handle core events for SSE streaming.

        Since only one execution runs at a time, we just need to check
        if we have an active SSE queue.
        """
        if not self._sse_queue:
            return

        if event.execution_id != self._current_execution_id:
            return

        queue = self._sse_queue

        sse_msg = None

        if isinstance(event, MessageEvent):
            sse_msg = SSEMessage(
                type=SSEMessageType.MESSAGE,
                data=SSEMessageData(
                    id=event.message.id,
                    role=event.message.role,
                    content=event.message.content,
                    timestamp=event.message.timestamp,
                ).model_dump(),
            )
        elif isinstance(event, ToolUseEvent):
            sse_msg = SSEMessage(
                type=SSEMessageType.ACTION,
                data=SSEActionData(
                    action=event.tool_use.action,
                    details=event.tool_use.details,
                ).model_dump(),
            )
        elif isinstance(event, StatusChangeEvent):
            sse_msg = SSEMessage(
                type=SSEMessageType.STATUS,
                data=SSEStatusData(status=event.new_status).model_dump(),
            )

            # Send completion event if done
            if event.new_status in (
                ExecutionStatus.COMPLETED,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED,
            ):
                await queue.put(sse_msg)
                completion_msg = SSEMessage(
                    type=SSEMessageType.COMPLETED,
                    data={"status": event.new_status.value},
                )
                await queue.put(completion_msg)
                await queue.put(None)  # signal end of stream
                return
        elif isinstance(event, ErrorEvent):
            sse_msg = SSEMessage(
                type=SSEMessageType.ERROR,
                data=SSEErrorData(error=event.error).model_dump(),
            )
        elif isinstance(event, IterationEvent):
            sse_msg = SSEMessage(
                type=SSEMessageType.ACTION,
                data=SSEActionData(
                    action="iteration",
                    details={"current": event.current, "max": event.max_iterations},
                ).model_dump(),
            )

        if sse_msg:
            await queue.put(sse_msg)
