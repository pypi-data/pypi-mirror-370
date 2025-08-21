import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, overload

from mirrai.core.agent.models import (
    DisplayConfig,
    TaskInput,
    TaskLike,
    TaskWithSystemPrompt,
    WindowSetup,
)
from mirrai.core.agent.tool_handler import ToolHandler
from mirrai.core.capture import ScreenCapture
from mirrai.core.constants import (
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROVIDER,
    WINDOW_FOCUS_DELAY,
)
from mirrai.core.execution.events import (
    ErrorEvent,
    ExecutionEventEmitter,
    IterationEvent,
    MessageEvent,
    StatusChangeEvent,
    ToolUseEvent,
)
from mirrai.core.execution.models import (
    ExecutionRequest,
    ExecutionStatus,
    Message,
    ToolUse,
)
from mirrai.core.input_controller.factory import InputControllerFactory
from mirrai.core.logger import logger
from mirrai.core.providers import (
    AIProvider,
    MessageRole,
    ProviderFactory,
    ProviderMessage,
    ProviderToolDefinition,
)
from mirrai.core.terminal.output import AgentOutput
from mirrai.core.window_manager.factory import WindowManagerFactory


class AgentExecution:
    """Represents a single execution of the agent."""

    @overload
    def __init__(
        self,
        request: ExecutionRequest,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        task: TaskInput,
        window: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        quiet: bool = False,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        model: Optional[str] = None,
        provider: str = DEFAULT_PROVIDER,
        provider_config: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def __init__(
        self,
        request: Optional[ExecutionRequest] = None,
        *,
        task: Optional[TaskInput] = None,
        window: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        quiet: bool = False,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        model: Optional[str] = None,
        provider: str = DEFAULT_PROVIDER,
        provider_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an agent execution."""
        if request is not None:
            self.cfg = request
        elif task is not None:
            task_system_prompt = None
            if isinstance(task, str):
                task_str = task
            elif isinstance(task, TaskLike):
                task_str = task.to_prompt()
                if isinstance(task, TaskWithSystemPrompt):
                    task_system_prompt = task.get_system_prompt()
            else:
                raise ValueError("Task must be a string or implement TaskLike protocol")

            full_system_prompt = system_prompt
            if task_system_prompt:
                if system_prompt:
                    full_system_prompt = f"{task_system_prompt}\n\n{system_prompt}"
                else:
                    full_system_prompt = task_system_prompt

            logger.debug(f"System prompt: {full_system_prompt}")
            self.cfg = ExecutionRequest(
                task=task_str,
                window=window,
                system_prompt=full_system_prompt,
                max_tokens=max_tokens,
                quiet=quiet,
                max_iterations=max_iterations,
                model=model,
                provider=provider,
                provider_config=provider_config,
            )
        else:
            raise ValueError('Either "request" or "task" must be provided')

        self.id = str(uuid.uuid4())
        self.request = self.cfg
        self.status = ExecutionStatus.IDLE
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Execution history for persistence and API responses
        # These lists track the execution with timestamps for audit/persistence
        self.execution_messages: List[Message] = []  # User/assistant text messages with timestamps
        self.tool_uses: List[ToolUse] = []  # Tool interactions with timestamps and details

        # LLM conversation state (the working message history for provider API calls).
        # This includes tool calls/results in the format expected by the LLM provider.
        self.messages: List[ProviderMessage] = []

        self.provider: AIProvider = ProviderFactory.create_provider(
            provider_type=self.cfg.provider,
            **(self.cfg.provider_config or {}),
        )

        self.window_manager = WindowManagerFactory.get()
        self.input_controller = InputControllerFactory.get()
        self.screen_capture = ScreenCapture()
        self.events = ExecutionEventEmitter()
        self.display = AgentOutput(quiet=self.cfg.quiet)

        self.window_setup: Optional[WindowSetup] = None
        self.display_config: DisplayConfig = DisplayConfig.from_screen()
        self.tool_handler: Optional[ToolHandler] = None
        self.current_iteration: int = 0
        self.max_iterations: int = self.cfg.max_iterations
        self.system_prompt: str = ""

    async def execute(self) -> List[ProviderMessage]:
        self.window_setup = self._setup_window(self.cfg.window)
        if self.window_setup is None:
            return []

        original_window = self.window_manager.get_focused_window()

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
        self.system_prompt = self.cfg.system_prompt or ""
        if not self.system_prompt:
            self.system_prompt = (
                "You are an AI desktop automation assistant. "
                "You can take screenshots and interact with the screen using mouse and keyboard."
            )

        self.messages = [ProviderMessage(role=MessageRole.USER, content=self.cfg.task)]

        self.display.show_message("user", self.cfg.task)

        await self.add_message("user", self.cfg.task)
        logger.debug(f"AgentExecution: Added user message to execution {self.id}")

        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1

            logger.debug(
                f"AgentExecution: Emitting IterationEvent for execution {self.id}: {self.current_iteration}/{self.max_iterations}"
            )
            await self.events.emit_async(
                IterationEvent(self.id, self.current_iteration, self.max_iterations)
            )

            should_continue = await self._execute_step()

            if not should_continue:
                break

        if self.current_iteration >= self.max_iterations:
            logger.warning(f"Reached maximum iterations ({self.cfg.max_iterations})")

        if original_window and self.cfg.window:
            self.window_manager.focus_window(original_window)
            logger.debug(f"Restored focus to original window: {original_window}")

        return self.messages

    async def _execute_step(self) -> bool:
        """Execute a single step of the agent loop.

        Returns:
            True if the loop should continue, False if it should stop.
        """
        try:

            tools: List[ProviderToolDefinition]
            if self.provider.supports_computer_use():
                tools = [dict(self.display_config.to_computer_tool())]
            else:
                tool_def = self.provider.format_tool_definition(
                    self.display_config.display_width_scaled,
                    self.display_config.display_height_scaled,
                )
                tools = [tool_def]

            if self.current_iteration == 1:
                logger.debug(f"Using provider: {self.provider.__class__.__name__}")
                logger.debug(f"Tool definitions: {tools}")

            model = self.cfg.model or self.provider.get_default_model()

            self.display.start_loading()

            response = await self.provider.create_completion(
                messages=self.messages,
                model=model,
                max_tokens=self.cfg.max_tokens,
                tools=tools,
                system_prompt=self.system_prompt,
            )

            self.display.stop_loading()

            assistant_message = ProviderMessage(role=MessageRole.ASSISTANT, content="")
            tool_results = []
            if response.content:
                assistant_message.content = response.content
                self.display.show_message("assistant", response.content)
                await self.add_message("assistant", response.content)
                logger.debug(f"AgentExecution: Added assistant message to execution {self.id}")

            if response.tool_calls:
                assistant_message.tool_calls = response.tool_calls
                for tool_call in response.tool_calls:
                    logger.debug(f"Tool request: {tool_call.name}, Args: {tool_call.arguments}")

                    action = tool_call.arguments.get("action", tool_call.name)
                    await self.add_tool_use(action, tool_call.arguments)
                    logger.debug(
                        f"AgentExecution: Added tool use to execution {self.id}: action={action}"
                    )

                    self.display.start_loading()
                    tool_result = await self._process_tool_call(tool_call)
                    self.display.stop_loading()

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
        finally:
            self.display.stop_loading()

    async def set_status(self, status: ExecutionStatus) -> None:
        """Update execution status and emit StatusChangeEvent."""
        old_status = self.status
        self.status = status

        if status == ExecutionStatus.RUNNING and self.started_at is None:
            self.started_at = datetime.now()
        elif status in (
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        ):
            if self.completed_at is None:
                self.completed_at = datetime.now()

        await self.events.emit_async(StatusChangeEvent(self.id, old_status, status))

    async def add_message(
        self, role: Literal["user", "assistant", "system"], content: str
    ) -> Message:
        """Add a message to the execution history and emit event."""
        message = Message(role=role, content=content)
        self.execution_messages.append(message)
        await self.events.emit_async(MessageEvent(self.id, message))
        return message

    async def add_tool_use(self, action: str, details: Dict[str, Any]) -> ToolUse:
        """Add a tool use to the execution history and emit event."""
        tool_use = ToolUse(action=action, details=details)
        self.tool_uses.append(tool_use)
        await self.events.emit_async(ToolUseEvent(self.id, tool_use))
        return tool_use

    async def set_error(self, error: str) -> None:
        """Set error message, mark as failed, and emit ErrorEvent."""
        self.error = error
        await self.set_status(ExecutionStatus.FAILED)
        await self.events.emit_async(ErrorEvent(self.id, error))

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
            self.display_config = DisplayConfig.from_screen()
            return WindowSetup()

        target_window = self.window_manager.find_window(window_spec)
        if not target_window:
            logger.error(f"Window matching spec '{window_spec}' not found")
            return None

        window_rect = self.window_manager.get_client_rect(target_window.window_id)
        if not window_rect:
            logger.error(f"Could not get window rect for '{window_spec}'")
            return None

        self.display_config = DisplayConfig.from_screen(
            width=window_rect.width, height=window_rect.height
        )

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

            if not self.cfg.quiet:
                self.display.show_focused_window(self.window_setup.window)

            await asyncio.sleep(WINDOW_FOCUS_DELAY)

            window_offset_x = self.window_setup.offset_x
            window_offset_y = self.window_setup.offset_y

        return ToolHandler(
            screen_capture=self.screen_capture,
            input_controller=self.input_controller,
            window_manager=self.window_manager,
            window_id=window_id,
            quiet=self.cfg.quiet,
            scale_factor=self.display_config.scale_factor,
            scaled_width=self.display_config.display_width_scaled,
            scaled_height=self.display_config.display_height_scaled,
            window_offset_x=window_offset_x,
            window_offset_y=window_offset_y,
            display=self.display,
        )
