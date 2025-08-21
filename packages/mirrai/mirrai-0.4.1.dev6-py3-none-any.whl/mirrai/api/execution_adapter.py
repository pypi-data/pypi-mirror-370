import asyncio
from typing import AsyncGenerator, Awaitable, Callable, Optional

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
from mirrai.core.execution.models import ExecutionRequest, ExecutionStatus

AsyncEventHandler = Callable[[ExecutionEvent], Awaitable[None]]


class APIExecutionManager:
    """Wraps core ExecutionManager with API-specific features like SSE."""

    def __init__(self):
        """Initialize API execution manager."""
        from mirrai.core.agent.execution import AgentExecution

        self.core_manager = ExecutionManager()
        self._sse_queue: Optional[asyncio.Queue[Optional[SSEMessage]]] = None
        self._current_execution_id: Optional[str] = None
        self._agent_event_handler: Optional[AsyncEventHandler] = None
        self._current_execution: Optional[AgentExecution] = None

    async def create_execution(self, request: ExecutionRequest):
        """Create and start a new execution."""
        from mirrai.core.logger import logger

        if self._current_execution and self._agent_event_handler:
            logger.debug(
                f"APIExecutionManager: Unsubscribing from previous execution {self._current_execution_id}"
            )
            self._current_execution.events.all.off_async(self._agent_event_handler)
            self._agent_event_handler = None

        execution = await self.core_manager.create_execution(request)
        self._sse_queue = asyncio.Queue()
        self._current_execution_id = execution.id
        self._current_execution = execution

        logger.debug(f"APIExecutionManager: Created execution {execution.id}")

        logger.debug(
            f"APIExecutionManager: Subscribing to AgentExecution.events for {execution.id}"
        )

        async def handle_agent_event(event):
            logger.debug(
                f"APIExecutionManager: Received {type(event).__name__} from execution {execution.id}"
            )
            await self._handle_event_for_sse(event)

        self._agent_event_handler = handle_agent_event
        execution.events.all.on_async(self._agent_event_handler)

        return execution

    async def get_execution(self, execution_id: str):
        """Get an execution by ID."""
        return await self.core_manager.get_execution(execution_id)

    async def list_executions(
        self,
        status: Optional[ExecutionStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list, int]:
        """List executions with optional filtering."""
        return await self.core_manager.list_executions(status, limit, offset)

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running execution."""
        await self.core_manager.cancel_execution(execution_id)

    async def stream_execution(self, execution_id: str) -> AsyncGenerator[SSEMessage, None]:
        """Stream SSE events for an execution."""
        try:
            execution = await self.get_execution(execution_id)
        except ExecutionNotFoundError:
            yield SSEMessage(type=SSEMessageType.ERROR, data={"error": "Execution not found"})
            return

        if execution_id != self._current_execution_id or not self._sse_queue:
            yield SSEMessage(type=SSEMessageType.ERROR, data={"error": "Not the current execution"})
            return

        queue = self._sse_queue

        if execution.status in (ExecutionStatus.IDLE, ExecutionStatus.STARTING):
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
                yield SSEMessage(type=SSEMessageType.KEEPALIVE, data={})  # keepalive

        if execution_id == self._current_execution_id:
            self._sse_queue = None
            self._current_execution_id = None

    async def _handle_event_for_sse(self, event: ExecutionEvent) -> None:
        """Handle core events for SSE streaming."""
        from mirrai.core.logger import logger

        logger.debug(
            f"APIExecutionManager._handle_event_for_sse: Received {type(event).__name__} for {event.execution_id}"
        )

        if not self._sse_queue:
            logger.debug("APIExecutionManager._handle_event_for_sse: No SSE queue, skipping")
            return

        if event.execution_id != self._current_execution_id:
            logger.debug(
                f"APIExecutionManager._handle_event_for_sse: Event for different execution ({event.execution_id} != {self._current_execution_id}), skipping"
            )
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
            logger.debug(
                f"APIExecutionManager._handle_event_for_sse: Queueing SSE message type={sse_msg.type.value}"
            )
            await queue.put(sse_msg)
        else:
            logger.debug(
                f"APIExecutionManager._handle_event_for_sse: No SSE message created for {type(event).__name__}"
            )
