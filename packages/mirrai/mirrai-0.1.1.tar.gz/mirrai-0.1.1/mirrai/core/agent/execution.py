"""Agent execution handling for isolated execution contexts."""

import asyncio
from typing import Any, Dict, List, Optional, cast, overload

from anthropic.types.beta import (
    BetaImageBlockParam,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlock,
    BetaToolUseBlockParam,
)

from mirrai.core.agent.models import DisplayConfig, WindowSetup
from mirrai.core.agent.tool_handler import ToolHandler
from mirrai.core.client import client
from mirrai.core.execution.events import (
    ExecutionEventEmitter,
    IterationEvent,
    MessageEvent,
    ToolUseEvent,
)
from mirrai.core.execution.models import ExecutionRequest
from mirrai.core.input_controller.factory import InputControllerFactory
from mirrai.core.logger import logger
from mirrai.core.screen_capture.factory import ScreenCaptureFactory
from mirrai.core.window_manager.factory import WindowManagerFactory

# "Computer use" beta flag - just predefined tool schemas and maybe a modified system prompt
# TODO: Consider using standard completions API via OpenRouter/Ollama
COMPUTER_USE_BETA_FLAG = "computer-use-2025-01-24"
WINDOW_FOCUS_DELAY = 0.5  # seconds to wait after focusing a window


class AgentExecution:
    """Represents a single execution of the agent."""

    @overload
    def __init__(
        self,
        request: ExecutionRequest,
    ) -> None:
        """Initialize from ExecutionRequest (for internal use)."""
        ...

    @overload
    def __init__(
        self,
        *,
        task: str,
        window: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        execute_actions: bool = True,
        debug_mode: bool = False,
        max_iterations: int = 50,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        """Initialize with parameters (for library use)."""
        ...

    def __init__(
        self,
        request: Optional[ExecutionRequest] = None,
        *,
        task: Optional[str] = None,
        window: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        execute_actions: bool = True,
        debug_mode: bool = False,
        max_iterations: int = 50,
        model: str = "claude-sonnet-4-20250514",
    ):
        """Initialize an agent execution.

        This constructor supports two usage patterns:
        1. Internal use: Pass an ExecutionRequest object directly
        2. Library use: Pass individual parameters with full type hints

        The overloaded signatures ensure proper type checking for both patterns.

        Args:
            request: ExecutionRequest object (for internal use)
            task: The task to perform (for library use)
            window: Optional window specifier (e.g., "chrome", "process:notepad")
            system_prompt: Optional custom system prompt
            max_tokens: Maximum tokens for the response (default: 4096)
            execute_actions: Whether to actually execute actions (default: True)
            debug_mode: Enable debug mode for verbose logging (default: False)
            max_iterations: Maximum number of agent iterations (default: 50)
            model: Anthropic model to use (default: claude-sonnet-4-20250514)
        """
        self.client = client.get_client()

        if request is not None:
            self.execution_config = request
        elif task is not None:
            self.execution_config = ExecutionRequest(
                task=task,
                window=window,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                execute_actions=execute_actions,
                debug_mode=debug_mode,
                max_iterations=max_iterations,
                model=model,
            )
        else:
            raise ValueError("Either 'request' or 'task' must be provided")

        self.events = ExecutionEventEmitter()
        self.window_manager = WindowManagerFactory.get()
        self.screen_capture = ScreenCaptureFactory.get()
        self.input_controller = InputControllerFactory.get()

        self.messages: List[BetaMessageParam] = []
        self.window_setup: Optional[WindowSetup] = None
        self.display_config: DisplayConfig = DisplayConfig.from_screen()
        self.tool_handler: Optional[ToolHandler] = None
        self.iteration_count: int = 0
        self.system_prompt: str = ""

    async def execute(self) -> List[BetaMessageParam]:
        """Execute this session."""
        self.window_setup = self._setup_window(self.execution_config.window)
        if self.window_setup is None:
            return []

        original_window = self.window_manager.get_focused_window()

        if self.execution_config.debug_mode:
            logger.debug(
                f"Actual screen resolution: {self.display_config.display_width}x{self.display_config.display_height}"
            )
            logger.debug(
                f"Scaled resolution sent to agent: {self.display_config.display_width_scaled}x{self.display_config.display_height_scaled}"
            )
            logger.debug(
                f"Scale factor: {self.display_config.scale_factor:.2f} (coordinates will be scaled by {1/self.display_config.scale_factor:.2f})"
            )

        self.tool_handler = await self._setup_tool_handler()
        self.system_prompt = self.execution_config.system_prompt or ""
        if not self.system_prompt:
            if self.execution_config.execute_actions:
                self.system_prompt = (
                    "You are an AI desktop automation assistant. "
                    "You can take screenshots and interact with the screen using mouse and keyboard."
                )
            else:
                self.system_prompt = (
                    "You are an AI desktop automation assistant. "
                    "You can take screenshots and interact with the screen. "
                    "Currently, mouse and keyboard actions are logged but not executed."
                )

        self.messages = [
            {
                "role": "user",
                "content": [BetaTextBlockParam(type="text", text=self.execution_config.task)],
            }
        ]

        # Don't send user message via callbacks - the client already knows what it sent
        # This prevents redundant messages in the SSE stream

        while self.iteration_count < self.execution_config.max_iterations:
            self.iteration_count += 1

            await self.events.emit_async(
                IterationEvent("agent", self.iteration_count, self.execution_config.max_iterations)
            )

            should_continue = await self._execute_step()

            if not should_continue:
                break

        if self.iteration_count >= self.execution_config.max_iterations:
            logger.warning(f"Reached maximum iterations ({self.execution_config.max_iterations})")

        if original_window and self.execution_config.window:
            self.window_manager.focus_window(original_window)
            logger.debug(f"Restored focus to original window: {original_window}")

        return self.messages

    async def _execute_step(self) -> bool:
        """Execute a single step of the agent loop.

        Returns:
            True if the loop should continue, False if it should stop.
        """
        try:
            from mirrai.core.execution.models import Message, ToolUse

            if self.execution_config.debug_mode and self.iteration_count == 1:
                tool_def = self.display_config.to_computer_tool()
                logger.debug(
                    f"Agent tool parameters: display_width_px={tool_def['display_width_px']}, display_height_px={tool_def['display_height_px']}"
                )

            response = await self.client.beta.messages.create(
                model=self.execution_config.model,
                max_tokens=self.execution_config.max_tokens,
                messages=self.messages,
                system=self.system_prompt,
                tools=[self.display_config.to_computer_tool()],
                betas=[COMPUTER_USE_BETA_FLAG],
            )

            assistant_content: List[BetaTextBlockParam | BetaToolUseBlockParam] = []
            tool_results: List[BetaToolResultBlockParam] = []

            for block in response.content:
                if isinstance(block, BetaTextBlock):
                    assistant_content.append(BetaTextBlockParam(type="text", text=block.text))
                    message = Message(role="assistant", content=block.text)
                    await self.events.emit_async(MessageEvent("agent", message))
                elif isinstance(block, BetaToolUseBlock):
                    logger.debug(f"Tool request: {block.name}, Input: {block.input}")
                    tool_input = cast(Dict[str, Any], block.input)
                    action = tool_input.get("action", block.name)
                    tool_use = ToolUse(action=action, details=tool_input)
                    await self.events.emit_async(ToolUseEvent("agent", tool_use))
                    tool_result = await self._process_tool_use(
                        block=block,
                        assistant_content=assistant_content,
                    )
                    tool_results.append(tool_result)

            self.messages.append(BetaMessageParam(role="assistant", content=assistant_content))

            if tool_results:
                self.messages.append(BetaMessageParam(role="user", content=tool_results))
                return True
            else:
                # TODO: Assess task completion via new tool calls
                # e.g., 'mark_task_complete', confidence of success (0 to 1) as param
                # < ~70% considered failed, < 90% triggers warning?
                logger.debug("Task completed (no more tool requests)")
                return False

        except Exception as e:
            logger.error(str(e))
            return False

    async def _process_tool_use(
        self,
        block: BetaToolUseBlock,
        assistant_content: List[BetaTextBlockParam | BetaToolUseBlockParam],
    ) -> BetaToolResultBlockParam:
        """Process a single tool use block and return the result."""
        # Handle the tool call
        tool_input = cast(Dict[str, Any], block.input)
        action = tool_input.get("action", "")

        if not action:
            result = {"error": "No action specified in tool input"}
        else:
            assert self.tool_handler is not None, "Tool handler not initialized"
            result = await self.tool_handler.handle(action, tool_input)

        # Add to assistant content
        assistant_content.append(
            BetaToolUseBlockParam(type="tool_use", id=block.id, name=block.name, input=block.input)
        )

        # Create appropriate tool result based on response type
        if "error" in result:
            return BetaToolResultBlockParam(
                type="tool_result",
                tool_use_id=block.id,
                content=result["error"],
                is_error=True,
            )
        elif "type" in result and result["type"] == "image":
            source_data = result.get("source", {})
            image_data = source_data.get("data", "") if isinstance(source_data, dict) else ""
            return BetaToolResultBlockParam(
                type="tool_result",
                tool_use_id=block.id,
                content=[
                    BetaImageBlockParam(
                        type="image",
                        source={
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    )
                ],
                is_error=False,
            )
        else:
            return BetaToolResultBlockParam(
                type="tool_result",
                tool_use_id=block.id,
                content=str(result),
                is_error=False,
            )

    def _setup_window(self, window_spec: Optional[str]) -> Optional[WindowSetup]:
        """Setup window configuration and display config.

        Returns:
            WindowSetup object or None if there was an error.
        """
        if not window_spec:
            # Full screen mode (empty setup)
            self.display_config = DisplayConfig.from_screen()
            return WindowSetup()

        # Window mode: find and setup the target window using spec
        target_window = self.window_manager.find_window(window_spec)
        if not target_window:
            logger.error(f"Window matching spec '{window_spec}' not found")
            return None

        # Get client rect (the inner content area, excluding window borders/titlebar)
        window_rect = self.window_manager.get_client_rect(target_window.window_id)
        if not window_rect:
            logger.error(f"Could not get window rect for '{window_spec}'")
            return None

        # Create display config with window dimensions
        self.display_config = DisplayConfig.from_screen(
            width=window_rect.width, height=window_rect.height
        )

        if self.execution_config.debug_mode:
            logger.debug(
                f"Window mode - using window dimensions: {window_rect.width}x{window_rect.height}"
            )
            logger.debug(f"Window position: ({window_rect.left}, {window_rect.top})")

        return WindowSetup(window=target_window, rect=window_rect)

    async def _setup_tool_handler(self) -> ToolHandler:
        """Setup the tool handler with necessary components."""
        window_id = None
        window_offset_x = 0
        window_offset_y = 0

        if self.window_setup and self.window_setup.is_window_mode and self.window_setup.window:
            window_id = self.window_setup.window.window_id

            # Focus the window
            self.window_manager.focus_window(window_id)
            logger.success(f"Focused window: {self.window_setup.window.title}")

            # Wait for window to be focused
            await asyncio.sleep(WINDOW_FOCUS_DELAY)

            window_offset_x = self.window_setup.offset_x
            window_offset_y = self.window_setup.offset_y

        return ToolHandler(
            screen_capture=self.screen_capture,
            input_controller=self.input_controller,
            window_manager=self.window_manager,
            window_id=window_id,
            execute_actions=self.execution_config.execute_actions,
            debug_mode=self.execution_config.debug_mode,
            scale_factor=self.display_config.scale_factor,
            scaled_width=self.display_config.display_width_scaled,
            scaled_height=self.display_config.display_height_scaled,
            window_offset_x=window_offset_x,
            window_offset_y=window_offset_y,
        )
