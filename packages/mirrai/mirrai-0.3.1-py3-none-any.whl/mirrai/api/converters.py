from mirrai.api.models import ExecutionResponse
from mirrai.core.execution.models import ExecutionState


def execution_state_to_api_response(execution: ExecutionState) -> ExecutionResponse:
    """Convert core ExecutionState to API ExecutionResponse."""
    return ExecutionResponse(
        execution_id=execution.id,
        status=execution.status,
        created_at=execution.created_at,
        task=execution.request.task,
        window=execution.request.window,
        messages=execution.messages,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        error=execution.error,
    )
