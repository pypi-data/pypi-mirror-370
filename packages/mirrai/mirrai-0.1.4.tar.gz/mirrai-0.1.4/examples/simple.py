import asyncio

# Requires ANTHROPIC_API_KEY environment variable to be set
from mirrai.core.agent import AgentExecution
from mirrai.core.execution.events.types import (
    IterationEvent,
    MessageEvent,
    ToolUseEvent,
)


async def handle_message(event: MessageEvent) -> None:
    print(f"{event.message.role}: {event.message.content}")


async def handle_tool_use(event: ToolUseEvent) -> None:
    print(f"Tool: {event.tool_use.action}")
    if event.tool_use.details:
        print(f"  Details: {event.tool_use.details}")


async def handle_iteration(event: IterationEvent) -> None:
    print(f"Iteration {event.current}/{event.max_iterations}")


async def main():
    execution = AgentExecution(
        task="Open a new tab in the notepad and enter a short story about cute dogs. Minimum 100 words.",
        window="process:Notepad",
    )

    execution.events.messages.on_async(handle_message)
    execution.events.tool_uses.on_async(handle_tool_use)
    execution.events.iterations.on_async(handle_iteration)

    await execution.execute()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
