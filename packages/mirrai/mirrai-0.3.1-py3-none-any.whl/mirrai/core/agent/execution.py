import asyncio
from typing import Any, Dict, List, Optional, overload

from mirrai.core.agent.models import DisplayConfig, WindowSetup
from mirrai.core.agent.tool_handler import ToolHandler
from mirrai.core.constants import DEFAULT_MAX_ITERATIONS, DEFAULT_MAX_TOKENS, WINDOW_FOCUS_DELAY
from mirrai.core.execution.events import (
    ExecutionEventEmitter,
    IterationEvent,
    MessageEvent,
    ToolUseEvent,
)
from mirrai.core.execution.models import ExecutionRequest
from mirrai.core.input_controller.factory import InputControllerFactory
from mirrai.core.logger import logger
from mirrai.core.providers import (
    AIProvider,
    MessageRole,
    ProviderFactory,
    ProviderMessage,
    ProviderToolDefinition,
)
from mirrai.core.screen_capture.factory import ScreenCaptureFactory
from mirrai.core.window_manager.factory import WindowManagerFactory


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
        max_tokens: int = DEFAULT_MAX_TOKENS,
        execute_actions: bool = True,
        debug_mode: bool = False,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        provider_config: Optional[Dict[str, Any]] = None,
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
        max_tokens: int = DEFAULT_MAX_TOKENS,
        execute_actions: bool = True,
        debug_mode: bool = False,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        provider_config: Optional[Dict[str, Any]] = None,
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
            max_tokens: Maximum tokens for the response
            execute_actions: Whether to actually execute actions (default: True)
            debug_mode: Enable debug mode for verbose logging (default: False)
            max_iterations: Maximum number of agent iterations
            model: Model to use
        """
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
                provider=provider,
                provider_config=provider_config,
            )
        else:
            raise ValueError("Either 'request' or 'task' must be provided")

        if not self.execution_config.provider:
            raise ValueError("Provider must be specified")

        self.provider: AIProvider = ProviderFactory.create_provider(
            provider_type=self.execution_config.provider,
            **(self.execution_config.provider_config or {}),
        )

        self.events = ExecutionEventEmitter()
        self.window_manager = WindowManagerFactory.get()
        self.screen_capture = ScreenCaptureFactory.get()
        self.input_controller = InputControllerFactory.get()

        self.messages: List[ProviderMessage] = []
        self.window_setup: Optional[WindowSetup] = None
        self.display_config: DisplayConfig = DisplayConfig.from_screen()
        self.tool_handler: Optional[ToolHandler] = None
        self.iteration_count: int = 0
        self.system_prompt: str = ""

    async def execute(self) -> List[ProviderMessage]:
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

        self.messages = [ProviderMessage(role=MessageRole.USER, content=self.execution_config.task)]

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

            tools: List[ProviderToolDefinition]
            if self.provider.supports_computer_use():
                tools = [dict(self.display_config.to_computer_tool())]
            else:
                tool_def = self.provider.format_tool_definition(
                    self.display_config.display_width_scaled,
                    self.display_config.display_height_scaled,
                )
                tools = [tool_def]

            if self.execution_config.debug_mode and self.iteration_count == 1:
                logger.debug(f"Using provider: {self.provider.__class__.__name__}")
                logger.debug(f"Tool definitions: {tools}")

            model = self.execution_config.model or self.provider.get_default_model()
            response = await self.provider.create_completion(
                messages=self.messages,
                model=model,
                max_tokens=self.execution_config.max_tokens,
                tools=tools,
                system_prompt=self.system_prompt,
            )

            assistant_message = ProviderMessage(role=MessageRole.ASSISTANT, content="")
            tool_results = []
            if response.content:
                assistant_message.content = response.content
                message = Message(role="assistant", content=response.content)
                await self.events.emit_async(MessageEvent("agent", message))

            if response.tool_calls:
                assistant_message.tool_calls = response.tool_calls
                for tool_call in response.tool_calls:
                    logger.debug(f"Tool request: {tool_call.name}, Args: {tool_call.arguments}")

                    action = tool_call.arguments.get("action", tool_call.name)
                    tool_use = ToolUse(action=action, details=tool_call.arguments)
                    await self.events.emit_async(ToolUseEvent("agent", tool_use))

                    tool_result = await self._process_tool_call(tool_call)
                    tool_results.append(tool_result)

            self.messages.append(assistant_message)

            if tool_results:
                tool_result_message = ProviderMessage(role=MessageRole.USER, content=tool_results)
                self.messages.append(tool_result_message)
                return True
            else:
                logger.debug("Task completed (no more tool requests)")
                return False

        except Exception as e:
            logger.error(str(e))
            return False

    async def _process_tool_call(self, tool_call) -> Dict[str, Any]:
        """Process a single tool call and return the result."""
        action = tool_call.arguments.get("action", "")
        if not action:
            return {"tool_call_id": tool_call.id, "error": "No action specified in tool input"}

        assert self.tool_handler is not None, "Tool handler not initialized"
        result = await self.tool_handler.handle(action, tool_call.arguments)

        if "error" in result:
            return {"tool_call_id": tool_call.id, "error": result["error"]}
        elif "type" in result and result["type"] == "image":
            source_data = result.get("source", {})
            image_data = source_data.get("data", "") if isinstance(source_data, dict) else ""
            return {"tool_call_id": tool_call.id, "content": {"type": "image", "data": image_data}}
        else:
            return {"tool_call_id": tool_call.id, "content": str(result)}

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

            self.window_manager.focus_window(window_id)
            logger.success(f"Focused window: {self.window_setup.window.title}")

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
