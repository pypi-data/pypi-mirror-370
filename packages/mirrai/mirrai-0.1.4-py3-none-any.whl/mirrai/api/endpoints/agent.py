from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from mirrai.api.converters import execution_state_to_api_response
from mirrai.api.execution_adapter import APIExecutionManager
from mirrai.api.models import (
    CreateExecutionResponse,
    ExecutionListResponse,
    ExecutionResponse,
    ExecutionStatus,
)
from mirrai.core.execution.exceptions import (
    ExecutionAlreadyRunningError,
    ExecutionNotFoundError,
    ExecutionNotRunningError,
)
from mirrai.core.execution.models import ExecutionRequest

router = APIRouter(prefix="/agent", tags=["agent"])


# Dependency to get execution manager (will be injected from main app)
def get_execution_manager() -> APIExecutionManager:
    """Get the execution manager instance."""
    # This will be overridden in main.py with the actual instance
    raise NotImplementedError("Execution manager not configured")


@router.post("/executions", response_model=CreateExecutionResponse)
async def create_execution(
    request: ExecutionRequest,
    manager: APIExecutionManager = Depends(get_execution_manager),
) -> CreateExecutionResponse:
    """Create a new agent execution."""
    try:
        execution = await manager.create_execution(request)

        return CreateExecutionResponse(
            execution_id=execution.id,
            status=execution.status,
            created_at=execution.created_at,
        )

    except ExecutionAlreadyRunningError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "An execution is already running",
                "active_execution_id": e.active_execution_id,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    manager: APIExecutionManager = Depends(get_execution_manager),
) -> ExecutionResponse:
    """Get full execution details."""
    try:
        execution = await manager.get_execution(execution_id)
        # Convert ExecutionState to ExecutionResponse
        return execution_state_to_api_response(execution)
    except ExecutionNotFoundError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.get("/executions", response_model=ExecutionListResponse)
async def list_executions(
    status: Optional[ExecutionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    manager: APIExecutionManager = Depends(get_execution_manager),
) -> ExecutionListResponse:
    """List all executions with optional filtering."""
    executions, total = await manager.list_executions(status, limit, offset)

    return ExecutionListResponse(
        executions=[execution_state_to_api_response(e) for e in executions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/executions/{execution_id}/stream")
async def stream_execution(
    execution_id: str,
    manager: APIExecutionManager = Depends(get_execution_manager),
):
    """
    Stream execution updates via Server-Sent Events (SSE).

    Returns a stream of events:
    - status: Execution status changes
    - message: Agent messages
    - action: Agent actions (click, type, etc.)
    - completed: Execution completed
    - error: Execution errors
    """
    try:
        await manager.get_execution(execution_id)  # Just verify it exists
    except ExecutionNotFoundError:
        raise HTTPException(status_code=404, detail="Execution not found")

    async def event_generator():
        """Generate SSE events."""
        async for event in manager.stream_execution(execution_id):
            yield event.to_sse_format()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.delete("/executions/{execution_id}")
async def cancel_execution(
    execution_id: str,
    manager: APIExecutionManager = Depends(get_execution_manager),
):
    """Cancel a running execution."""
    try:
        await manager.cancel_execution(execution_id)
        return {"message": "Execution cancelled", "execution_id": execution_id}
    except ExecutionNotFoundError:
        raise HTTPException(status_code=404, detail="Execution not found")
    except ExecutionNotRunningError as e:
        raise HTTPException(
            status_code=409, detail=f"Execution is not running (status: {e.status})"
        )
