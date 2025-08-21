import asyncio
import os
from typing import List, Optional, Tuple

import pytweening

from mirrai.core.constants import IS_LINUX, SHORT_DISTANCE_THRESHOLD, TYPING_DELAY_MS
from mirrai.core.utils.common import calc_distance, calc_move_duration

if IS_LINUX:
    from pynput import keyboard, mouse  # type: ignore
    from pynput.keyboard import Key  # type: ignore
    from pynput.mouse import Button  # type: ignore

from mirrai.core.input_controller.base import (
    InputController,
    KeyModifier,
    MouseButton,
    ScrollDirection,
)
from mirrai.core.logger import logger


class LinuxInputController(InputController):
    """Linux implementation of InputController using pynput."""

    def __init__(self):
        self._check_display_server()
        self._mouse = mouse.Controller()
        self._keyboard = keyboard.Controller()
        self._button_map = self._build_button_map()
        self._key_map = self._build_key_map()

    def _check_display_server(self) -> None:
        """Check if running on X11 or Wayland and raise error if Wayland."""
        if "WAYLAND_DISPLAY" in os.environ:
            logger.error("Wayland detected but not supported for input control (pynput)")
            raise NotImplementedError("Wayland is not yet supported.")

        if "DISPLAY" not in os.environ:
            logger.error("No DISPLAY environment variable found")
            raise RuntimeError("X11 display not found. Input control requires X11.")

    async def click(
        self,
        x: int,
        y: int,
        button: MouseButton = MouseButton.LEFT,
        double_click: bool = False,
        triple_click: bool = False,
    ) -> bool:
        try:
            await self._smooth_move_to(x, y)

            pynput_button = self._get_button(button)

            if triple_click:
                for _ in range(3):
                    self._mouse.click(pynput_button)
                    await asyncio.sleep(0.05)
            elif double_click:
                self._mouse.click(pynput_button, 2)
            else:
                self._mouse.click(pynput_button)

            return True
        except Exception as e:
            logger.debug(f"Click error: {e}")
            return False

    async def mouse_down(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        try:
            await self._smooth_move_to(x, y)
            pynput_button = self._get_button(button)
            self._mouse.press(pynput_button)
            return True
        except Exception:
            return False

    async def mouse_up(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        try:
            await self._smooth_move_to(x, y)
            pynput_button = self._get_button(button)
            self._mouse.release(pynput_button)
            return True
        except Exception:
            return False

    async def mouse_move(self, x: int, y: int, duration: float = 0.0) -> bool:
        try:
            if duration > 0:
                start_x, start_y = self._mouse.position
                steps = max(int(duration * 60), 10)

                distance = calc_distance(start_x, start_y, x, y)
                easing_func = (
                    pytweening.easeOutExpo
                    if distance < SHORT_DISTANCE_THRESHOLD
                    else pytweening.easeInOutSine
                )

                for i in range(steps + 1):
                    progress = i / steps
                    eased_progress = easing_func(progress)

                    inter_x = start_x + (x - start_x) * eased_progress
                    inter_y = start_y + (y - start_y) * eased_progress

                    self._mouse.position = (int(inter_x), int(inter_y))
                    if i < steps:
                        await asyncio.sleep(duration / steps)
            else:
                self._mouse.position = (x, y)

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
            await self._smooth_move_to(start_x, start_y)
            pynput_button = self._get_button(button)
            self._mouse.press(pynput_button)
            await self.mouse_move(end_x, end_y, duration)
            self._mouse.release(pynput_button)

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
                await self._smooth_move_to(x, y)

            if direction == ScrollDirection.UP:
                self._mouse.scroll(0, amount)
            elif direction == ScrollDirection.DOWN:
                self._mouse.scroll(0, -amount)
            elif direction == ScrollDirection.LEFT:
                self._mouse.scroll(-amount, 0)
            elif direction == ScrollDirection.RIGHT:
                self._mouse.scroll(amount, 0)

            return True
        except Exception:
            return False

    async def type_text(self, text: str, delay_ms: int = TYPING_DELAY_MS) -> bool:
        try:
            for char in text:
                self._keyboard.type(char)
                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)
            return True
        except Exception:
            return False

    async def key_press(self, key: str, modifiers: Optional[KeyModifier] = None) -> bool:
        try:
            # Collect modifier keys
            modifier_keys = []
            if modifiers:
                if modifiers.ctrl:
                    modifier_keys.append(Key.ctrl)
                if modifiers.alt:
                    modifier_keys.append(Key.alt)
                if modifiers.shift:
                    modifier_keys.append(Key.shift)
                if modifiers.meta:  # Super/Windows key
                    modifier_keys.append(Key.cmd)

            # Map key to pynput format
            mapped_key = self._map_key(key)

            # Press with modifiers
            if modifier_keys:
                with self._keyboard.pressed(*modifier_keys):
                    self._keyboard.press(mapped_key)
                    self._keyboard.release(mapped_key)
            else:
                self._keyboard.press(mapped_key)
                self._keyboard.release(mapped_key)

            return True
        except Exception:
            return False

    async def key_down(self, key: str) -> bool:
        try:
            mapped_key = self._map_key(key)
            self._keyboard.press(mapped_key)
            return True
        except Exception:
            return False

    async def key_up(self, key: str) -> bool:
        try:
            mapped_key = self._map_key(key)
            self._keyboard.release(mapped_key)
            return True
        except Exception:
            return False

    async def hotkey(self, keys: List[str]) -> bool:
        try:
            mapped_keys = [self._map_key(k) for k in keys]

            # Press all keys
            for key in mapped_keys:
                self._keyboard.press(key)

            # Release all keys in reverse order
            for key in reversed(mapped_keys):
                self._keyboard.release(key)

            return True
        except Exception:
            return False

    async def get_mouse_position(self) -> Tuple[int, int]:
        pos = self._mouse.position
        return (int(pos[0]), int(pos[1]))

    async def _smooth_move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move cursor smoothly to target position with human-like motion."""
        if duration is None:
            current_pos = await self.get_mouse_position()
            duration = calc_move_duration(x, y, current_pos[0], current_pos[1])

        await self.mouse_move(x, y, duration=duration)

    def _get_button(self, button: MouseButton) -> Button:
        """Convert MouseButton enum to pynput Button."""
        return self._button_map.get(button, Button.left)

    def _map_key(self, key: str):
        """Map key string to pynput Key or character."""
        key_lower = key.lower()

        # Check if it's in our key map (special keys)
        if key_lower in self._key_map:
            return self._key_map[key_lower]

        # Single character
        if len(key) == 1:
            return key

        # Try to get it as a Key attribute
        try:
            return getattr(Key, key_lower)
        except AttributeError:
            # Return as-is and hope pynput handles it
            return key

    def _build_button_map(self) -> dict:
        """Build mapping of MouseButton to pynput Button."""
        return {
            MouseButton.LEFT: Button.left,
            MouseButton.RIGHT: Button.right,
            MouseButton.MIDDLE: Button.middle,
        }

    def _build_key_map(self) -> dict:
        """Build mapping of common key names to pynput Keys."""
        return {
            "enter": Key.enter,
            "return": Key.enter,
            "tab": Key.tab,
            "space": Key.space,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "escape": Key.esc,
            "esc": Key.esc,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "home": Key.home,
            "end": Key.end,
            "pageup": Key.page_up,
            "pagedown": Key.page_down,
            "f1": Key.f1,
            "f2": Key.f2,
            "f3": Key.f3,
            "f4": Key.f4,
            "f5": Key.f5,
            "f6": Key.f6,
            "f7": Key.f7,
            "f8": Key.f8,
            "f9": Key.f9,
            "f10": Key.f10,
            "f11": Key.f11,
            "f12": Key.f12,
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "alt": Key.alt,
            "shift": Key.shift,
            "cmd": Key.cmd,
            "win": Key.cmd,
            "windows": Key.cmd,
            "meta": Key.cmd,
            "super": Key.cmd,
        }
