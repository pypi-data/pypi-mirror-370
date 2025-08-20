import asyncio
import base64
import os
import tempfile
import webbrowser
from io import BytesIO
from typing import Any, Dict, Optional

from PIL import Image
from rich.prompt import Confirm

from mirrai.core.agent.output import AgentOutput
from mirrai.core.capture import ScreenCapture
from mirrai.core.constants import WINDOW_FOCUS_ENSURE_DELAY
from mirrai.core.input_controller.base import InputController, MouseButton, ScrollDirection
from mirrai.core.logger import logger
from mirrai.core.utils.common import format_bytes
from mirrai.core.window_manager.base import WindowManager


class ToolHandler:
    """Handles agent tool actions for desktop automation."""

    def __init__(
        self,
        screen_capture: ScreenCapture,
        input_controller: InputController,
        window_manager: WindowManager,
        window_id: Optional[int] = None,
        quiet: bool = False,
        debug_mode: bool = False,
        scale_factor: float = 1.0,
        scaled_width: Optional[int] = None,
        scaled_height: Optional[int] = None,
        window_offset_x: int = 0,
        window_offset_y: int = 0,
        display: Optional[AgentOutput] = None,
    ):
        self.screen_capture = screen_capture
        self.input_controller = input_controller
        self.window_manager = window_manager
        self.window_id = window_id
        self.quiet = quiet
        self.debug_mode = debug_mode
        self.scale_factor = scale_factor
        self.scaled_width = scaled_width
        self.scaled_height = scaled_height
        self.window_offset_x = window_offset_x
        self.window_offset_y = window_offset_y
        self.display = display or AgentOutput(quiet=quiet)

        self.action_map = {
            "screenshot": self.handle_screenshot,
            "left_click": self.handle_left_click,
            "right_click": self.handle_right_click,
            "double_click": self.handle_double_click,
            "triple_click": self.handle_triple_click,
            "type": self.handle_type,
            "key": self.handle_key,
            "mouse_move": self.handle_mouse_move,
            "scroll": self.handle_scroll,
            "wait": self.handle_wait,
        }

    async def _ensure_window_focus(self) -> None:
        """Ensure the target window is focused before mouse actions."""
        if self.window_id:
            self.window_manager.focus_window(self.window_id)
            await asyncio.sleep(WINDOW_FOCUS_ENSURE_DELAY)

    async def handle(self, action: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Route action to appropriate handler."""
        handler = self.action_map.get(action)
        if not handler:
            logger.error(f"Unknown action: {action}")
            return {"error": f"Unknown action: {action}"}
        return await handler(tool_input)

    async def handle_screenshot(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle screenshot action."""
        _ = tool_input

        if self.window_id:
            image_array = self.screen_capture.capture_window(self.window_id, use_client_area=True)
        else:
            image_array = self.screen_capture.capture_screen()

        if image_array is None:
            return {"error": "Failed to capture screen"}

        image = Image.fromarray(image_array)
        original_width, original_height = image.width, image.height

        needs_scaling = (
            self.scaled_width
            and self.scaled_height
            and (self.scaled_width != original_width or self.scaled_height != original_height)
        )

        if needs_scaling and self.scaled_width and self.scaled_height:
            logger.debug(f"Original screenshot: {original_width}x{original_height}")
            logger.debug(f"Scaling to: {self.scaled_width}x{self.scaled_height}")
            image = image.resize((self.scaled_width, self.scaled_height), Image.Resampling.LANCZOS)
            final_width, final_height = self.scaled_width, self.scaled_height
            scaled_from = (original_width, original_height)
        else:
            final_width, final_height = original_width, original_height
            scaled_from = None

        # Debug mode: save and show screenshot before sending
        if self.debug_mode:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                image.save(tmp_path, format="PNG")
                logger.warning(f"Screenshot saved to: {tmp_path}")

                try:
                    webbrowser.open(f"file://{os.path.abspath(tmp_path)}")
                    logger.warning("Opening screenshot in default viewer...")
                except Exception:
                    logger.warning("Could not open image viewer automatically.")

                if not Confirm.ask("[bold yellow]Send this screenshot to the agent?[/bold yellow]"):
                    logger.error("Screenshot cancelled by user")
                    return {"error": "Screenshot cancelled by user"}

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        base64_image = base64.b64encode(image_bytes).decode()

        data_size = format_bytes(len(image_bytes))

        self.display.show_screenshot(final_width, final_height, data_size, scaled_from=scaled_from)

        return {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": base64_image},
        }

    async def handle_left_click(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle left click action."""
        coordinate = tool_input.get("coordinate", [0, 0])

        actual_x = round(coordinate[0] / self.scale_factor) + self.window_offset_x
        actual_y = round(coordinate[1] / self.scale_factor) + self.window_offset_y

        logger.debug(
            f"Agent coordinate: {coordinate}, Window-relative: [{round(coordinate[0] / self.scale_factor)}, {round(coordinate[1] / self.scale_factor)}], Screen absolute: [{actual_x}, {actual_y}]"
        )

        self.display.show_click(
            MouseButton.LEFT,
            coordinate,
            actual_coord=(actual_x, actual_y),
            offset=(self.window_offset_x, self.window_offset_y),
        )

        await self._ensure_window_focus()
        success = await self.input_controller.click(actual_x, actual_y)
        return {
            "status": "success" if success else "failed",
            "action": "left_click",
            "coordinate": coordinate,
        }

    async def handle_right_click(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle right click action."""
        coordinate = tool_input.get("coordinate", [0, 0])

        actual_x = round(coordinate[0] / self.scale_factor) + self.window_offset_x
        actual_y = round(coordinate[1] / self.scale_factor) + self.window_offset_y

        logger.debug(f"Agent coordinate: {coordinate}, Actual coordinate: [{actual_x}, {actual_y}]")

        self.display.show_click(
            MouseButton.RIGHT,
            coordinate,
            actual_coord=(actual_x, actual_y),
            offset=(self.window_offset_x, self.window_offset_y),
        )

        await self._ensure_window_focus()
        success = await self.input_controller.click(actual_x, actual_y, MouseButton.RIGHT)
        return {
            "status": "success" if success else "failed",
            "action": "right_click",
            "coordinate": coordinate,
        }

    async def handle_double_click(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle double click action."""
        coordinate = tool_input.get("coordinate", [0, 0])

        actual_x = round(coordinate[0] / self.scale_factor) + self.window_offset_x
        actual_y = round(coordinate[1] / self.scale_factor) + self.window_offset_y

        logger.debug(f"Agent coordinate: {coordinate}, Actual coordinate: [{actual_x}, {actual_y}]")

        self.display.show_click(
            MouseButton.DOUBLE,
            coordinate,
            actual_coord=(actual_x, actual_y),
            offset=(self.window_offset_x, self.window_offset_y),
        )

        await self._ensure_window_focus()
        success = await self.input_controller.click(actual_x, actual_y, double_click=True)
        return {
            "status": "success" if success else "failed",
            "action": "double_click",
            "coordinate": coordinate,
        }

    async def handle_triple_click(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle triple click action."""
        coordinate = tool_input.get("coordinate", [0, 0])

        logger.warning(f"Triple-click requested at {coordinate}; not yet implemented. ")

        return {
            "error": "triple_click not yet implemented.",
            "action": "triple_click",
            "coordinate": coordinate,
        }

    async def handle_type(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle type text action."""
        text = tool_input.get("text", "")

        self.display.show_typing(text)

        success = await self.input_controller.type_text(text)
        return {"status": "success" if success else "failed", "action": "type", "text": text}

    async def handle_key(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key press action."""
        key = tool_input.get("text", "")

        self.display.show_key_press(key)

        success = await self.input_controller.key_press(key)
        return {"status": "success" if success else "failed", "action": "key", "key": key}

    async def handle_mouse_move(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mouse move action."""
        coordinate = tool_input.get("coordinate", [0, 0])

        actual_x = round(coordinate[0] / self.scale_factor) + self.window_offset_x
        actual_y = round(coordinate[1] / self.scale_factor) + self.window_offset_y

        logger.debug(f"Agent coordinate: {coordinate}, Actual coordinate: [{actual_x}, {actual_y}]")

        self.display.show_mouse_move(
            coordinate,
            actual_coord=(actual_x, actual_y),
            offset=(self.window_offset_x, self.window_offset_y),
        )

        await self._ensure_window_focus()
        success = await self.input_controller.mouse_move(actual_x, actual_y)
        return {
            "status": "success" if success else "failed",
            "action": "mouse_move",
            "coordinate": coordinate,
        }

    async def handle_scroll(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scroll action."""
        direction = tool_input.get("scroll_direction", "down")
        amount = tool_input.get("scroll_amount", 3)

        direction_map = {
            "up": ScrollDirection.UP,
            "down": ScrollDirection.DOWN,
            "left": ScrollDirection.LEFT,
            "right": ScrollDirection.RIGHT,
        }
        scroll_dir = direction_map.get(direction, ScrollDirection.DOWN)

        self.display.show_scroll(scroll_dir, amount)

        await self._ensure_window_focus()
        success = await self.input_controller.scroll(scroll_dir, amount)
        return {
            "status": "success" if success else "failed",
            "action": "scroll",
            "direction": direction,
            "amount": amount,
        }

    async def handle_wait(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle wait action."""
        duration = tool_input.get("duration", 1)

        self.display.show_wait(duration)

        await asyncio.sleep(duration)
        return {"status": "completed", "action": "wait", "duration": duration}
