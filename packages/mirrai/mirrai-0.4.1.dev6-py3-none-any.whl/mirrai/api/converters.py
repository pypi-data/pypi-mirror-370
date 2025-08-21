from mirrai.api.models import ExecutionResponse
from mirrai.core.agent.execution import AgentExecution


def agent_execution_to_api_response(execution: AgentExecution) -> ExecutionResponse:
    """Convert AgentExecution to API ExecutionResponse."""
    # TODO: Consider including tool_uses in the API response to provide
    # complete execution history including tool interactions
    return ExecutionResponse(
        execution_id=execution.id,
        status=execution.status,
        created_at=execution.created_at,
        task=execution.request.task,
        window=execution.request.window,
        messages=execution.execution_messages,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        error=execution.error,
    )
