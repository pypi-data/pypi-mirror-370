from typing import Dict, List, Optional, Tuple

import pyautogui
import pytweening

from mirrai.core.input_controller.base import (
    InputController,
    KeyModifier,
    MouseButton,
    ScrollDirection,
)
from mirrai.core.logger import logger
from mirrai.core.utils import (
    SHORT_DISTANCE_THRESHOLD,
    calc_distance,
    calc_move_duration,
)

pyautogui.FAILSAFE = False  # moving mouse to corner won't abort
pyautogui.PAUSE = 0.01  # minimal pause between actions
WINDOWS_SCROLL_UNIT = 120


class WindowsInputController(InputController):
    """Windows implementation of InputController using pyautogui."""

    def __init__(self):
        self._key_map = self._build_key_map()
        self._button_map = self._build_button_map()

    async def click(
        self,
        x: int,
        y: int,
        button: MouseButton = MouseButton.LEFT,
        double_click: bool = False,
        triple_click: bool = False,
    ) -> bool:
        try:
            button_str = self._get_button_string(button)

            # Move to position smoothly first
            self._smooth_move_to(x, y)

            if triple_click:
                pyautogui.click(button=button_str, clicks=3, interval=0.05)
            elif double_click:
                pyautogui.doubleClick(button=button_str)
            else:
                pyautogui.click(button=button_str)

            return True
        except Exception as e:
            logger.debug(f"Click error: {e}")
            return False

    async def mouse_down(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        try:
            button_str = self._get_button_string(button)

            # Move to position smoothly first
            self._smooth_move_to(x, y)
            pyautogui.mouseDown(button=button_str)
            return True
        except Exception:
            return False

    async def mouse_up(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        try:
            button_str = self._get_button_string(button)

            # Move to position smoothly first
            self._smooth_move_to(x, y)
            pyautogui.mouseUp(button=button_str)
            return True
        except Exception:
            return False

    async def mouse_move(self, x: int, y: int, duration: float = 0.0) -> bool:
        try:
            # Use provided duration or calculate automatically
            self._smooth_move_to(x, y, duration if duration > 0 else None)
            return True
        except Exception:
            return False

    async def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        button: MouseButton = MouseButton.LEFT,
        duration: float = 0.5,
    ) -> bool:
        try:
            button_str = self._get_button_string(button)

            # Move to start position smoothly
            self._smooth_move_to(start_x, start_y)

            # Then drag to end position (always use smooth easing for drags)
            pyautogui.dragTo(
                end_x, end_y, duration=duration, button=button_str, tween=pytweening.easeInOutSine
            )
            return True
        except Exception:
            return False

    async def scroll(
        self,
        direction: ScrollDirection,
        amount: int = 3,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> bool:
        try:
            if x is not None and y is not None:
                # Move to position smoothly before scrolling
                self._smooth_move_to(x, y)

            scroll_amount = amount * WINDOWS_SCROLL_UNIT

            if direction == ScrollDirection.UP:
                pyautogui.scroll(scroll_amount)
            elif direction == ScrollDirection.DOWN:
                pyautogui.scroll(-scroll_amount)
            elif direction == ScrollDirection.LEFT:
                pyautogui.hscroll(-scroll_amount)
            elif direction == ScrollDirection.RIGHT:
                pyautogui.hscroll(scroll_amount)

            return True
        except Exception:
            return False

    async def type_text(self, text: str, delay_ms: int = 12) -> bool:
        try:
            interval = delay_ms / 1000.0 if delay_ms > 0 else 0
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception:
            return False

    async def key_press(self, key: str, modifiers: Optional[KeyModifier] = None) -> bool:
        try:
            keys_to_press = []

            if modifiers:
                if modifiers.ctrl:
                    keys_to_press.append("ctrl")
                if modifiers.alt:
                    keys_to_press.append("alt")
                if modifiers.shift:
                    keys_to_press.append("shift")
                if modifiers.meta:  # Windows key
                    keys_to_press.append("win")

            # Map key name to pyautogui format
            key_mapped = self._map_key_to_pyautogui(key)
            keys_to_press.append(key_mapped)

            if len(keys_to_press) > 1:
                pyautogui.hotkey(*keys_to_press)
            else:
                pyautogui.press(key_mapped)

            return True
        except Exception:
            return False

    async def key_down(self, key: str) -> bool:
        try:
            key_mapped = self._map_key_to_pyautogui(key)
            pyautogui.keyDown(key_mapped)
            return True
        except Exception:
            return False

    async def key_up(self, key: str) -> bool:
        try:
            key_mapped = self._map_key_to_pyautogui(key)
            pyautogui.keyUp(key_mapped)
            return True
        except Exception:
            return False

    async def hotkey(self, keys: List[str]) -> bool:
        try:
            mapped_keys = [self._map_key_to_pyautogui(k) for k in keys]
            pyautogui.hotkey(*mapped_keys)
            return True
        except Exception:
            return False

    async def get_mouse_position(self) -> Tuple[int, int]:
        return pyautogui.position()

    def _smooth_move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move cursor smoothly to target position with human-like motion.

        Args:
            x, y: Target coordinates
            duration: Optional duration override (if None, calculates automatically)
        """
        # Get current position for distance calculation
        current_pos = pyautogui.position()

        # Calculate duration if not provided
        if duration is None:
            if current_pos:
                duration = calc_move_duration(x, y, current_pos[0], current_pos[1])
            else:
                duration = calc_move_duration(x, y)

        # Choose easing based on distance
        if current_pos:
            distance = calc_distance(current_pos[0], current_pos[1], x, y)
            easing = (
                pytweening.easeOutExpo
                if distance < SHORT_DISTANCE_THRESHOLD
                else pytweening.easeInOutSine
            )
        else:
            easing = pytweening.easeOutExpo

        # Perform the movement
        pyautogui.moveTo(x, y, duration=duration, tween=easing)

    def _get_button_string(self, button: MouseButton) -> str:
        """Convert MouseButton enum to pyautogui button string."""
        return self._button_map.get(button, "left")

    def _map_key_to_pyautogui(self, key: str) -> str:
        """Map a key name to pyautogui format."""
        key_lower = key.lower()
        return self._key_map.get(key_lower, key)

    def _build_button_map(self) -> Dict[MouseButton, str]:
        """Build mapping of MouseButton enum to pyautogui button strings."""
        return {
            MouseButton.LEFT: "left",
            MouseButton.RIGHT: "right",
            MouseButton.MIDDLE: "middle",
        }

    def _build_key_map(self) -> Dict[str, str]:
        """Build mapping of common key names."""
        return {
            "enter": "enter",
            "return": "enter",
            "tab": "tab",
            "space": "space",
            "backspace": "backspace",
            "delete": "delete",
            "escape": "esc",
            "esc": "esc",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
            "f1": "f1",
            "f2": "f2",
            "f3": "f3",
            "f4": "f4",
            "f5": "f5",
            "f6": "f6",
            "f7": "f7",
            "f8": "f8",
            "f9": "f9",
            "f10": "f10",
            "f11": "f11",
            "f12": "f12",
            "ctrl": "ctrl",
            "control": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "cmd": "win",
            "win": "win",
            "windows": "win",
            "meta": "win",
        }
