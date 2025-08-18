"""Example: Using Mirrai as a library."""

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
        task="On the left hand side of the screen, you will notice there is a list of passkeys. Select the one which says 'tom-rolling' in the name. Then, on the right hand side of the screen, click the button to set up other devices. A modal will pop up. Click yes to confirm. After that, you will see a screen to enter a 9 digit code. Click the 'Close' button to cancel the extension. All actions will be instant, so you dont need to do any waits.",
        window="process:BeyondIdentity",
    )

    execution.events.messages.on_async(handle_message)
    execution.events.tool_uses.on_async(handle_tool_use)
    execution.events.iterations.on_async(handle_iteration)

    await execution.execute()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
