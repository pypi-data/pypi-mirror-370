import asyncio
from typing import List, Literal, Optional, Tuple

import pytweening

from mirrai.core.constants import IS_MACOS, SHORT_DISTANCE_THRESHOLD, TYPING_DELAY_MS
from mirrai.core.utils.macos_permissions import MacOSPermissions

if IS_MACOS:
    # Core Graphics: https://developer.apple.com/documentation/coregraphics
    # AppKit: https://developer.apple.com/documentation/appkit
    # ApplicationServices: https://developer.apple.com/documentation/applicationservices

    # PyObjC provides Python bindings for macOS frameworks but lacks complete type stubs.
    # We need to ignore basedpyright errors for these.

    from AppKit import NSEvent  # type: ignore
    from AppKit import (  # type: ignore
        NSShiftKeyMask,  # type: ignore
        NSControlKeyMask,  # type: ignore
        NSAlternateKeyMask,  # type: ignore
        NSCommandKeyMask,  # type: ignore
    )
    from Quartz.CoreGraphics import (  # type: ignore
        CGEventCreate,  # type: ignore
        CGEventCreateKeyboardEvent,  # type: ignore
        CGEventCreateMouseEvent,  # type: ignore
        CGEventCreateScrollWheelEvent,  # type: ignore
        CGEventGetLocation,  # type: ignore
        CGEventPost,  # type: ignore
        CGEventSetFlags,  # type: ignore
        CGEventSetIntegerValueField,  # type: ignore
        CGEventSourceCreate,  # type: ignore
        CGEventSourceSetLocalEventsSuppressionInterval,  # type: ignore
        CGPointMake,  # type: ignore
        kCGEventLeftMouseDown,  # type: ignore
        kCGEventLeftMouseDragged,  # type: ignore
        kCGEventLeftMouseUp,  # type: ignore
        kCGEventMouseMoved,  # type: ignore
        kCGEventRightMouseDown,  # type: ignore
        kCGEventRightMouseUp,  # type: ignore
        kCGEventRightMouseDragged,  # type: ignore
        kCGEventOtherMouseDown,  # type: ignore
        kCGEventOtherMouseUp,  # type: ignore
        kCGEventOtherMouseDragged,  # type: ignore
        kCGEventSourceStateHIDSystemState,  # type: ignore
        kCGHIDEventTap,  # type: ignore
        kCGMouseButtonLeft,  # type: ignore
        kCGMouseButtonRight,  # type: ignore
        kCGMouseButtonCenter,  # type: ignore
        kCGMouseEventClickState,  # type: ignore
        kCGScrollEventUnitLine,  # type: ignore
    )

from mirrai.core.input_controller.base import (
    InputController,
    KeyModifier,
    MouseButton,
    ScrollDirection,
)
from mirrai.core.logger import logger
from mirrai.core.utils.common import calc_distance, calc_move_duration


class MacOSInputController(InputController):
    """macOS implementation of InputController using Quartz Core Graphics."""

    def __init__(self):
        MacOSPermissions.ensure_accessibility()
        self._event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
        self._key_map = self._build_key_map()
        self._modifier_map = self._build_modifier_map()

        # Reduce delay between events for smoother operation
        CGEventSourceSetLocalEventsSuppressionInterval(self._event_source, 0.0)

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
            point = CGPointMake(x, y)

            down_type, button_num = self._get_button_event_info(button, "down")
            up_type, _ = self._get_button_event_info(button, "up")

            click_count = 3 if triple_click else (2 if double_click else 1)
            for i in range(click_count):
                down_event = CGEventCreateMouseEvent(
                    self._event_source, down_type, point, button_num
                )

                CGEventSetIntegerValueField(down_event, kCGMouseEventClickState, i + 1)
                CGEventPost(kCGHIDEventTap, down_event)

                up_event = CGEventCreateMouseEvent(self._event_source, up_type, point, button_num)
                CGEventSetIntegerValueField(up_event, kCGMouseEventClickState, i + 1)
                CGEventPost(kCGHIDEventTap, up_event)

                if i < click_count - 1:
                    await asyncio.sleep(0.05)

            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.click error: {e}")
            return False

    async def mouse_down(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        try:
            await self._smooth_move_to(x, y)
            point = CGPointMake(x, y)

            event_type, button_num = self._get_button_event_info(button, "down")
            event = CGEventCreateMouseEvent(self._event_source, event_type, point, button_num)

            CGEventPost(kCGHIDEventTap, event)
            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.mouse_down error: {e}")
            return False

    async def mouse_up(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        try:
            await self._smooth_move_to(x, y)
            point = CGPointMake(x, y)

            event_type, button_num = self._get_button_event_info(button, "up")
            event = CGEventCreateMouseEvent(self._event_source, event_type, point, button_num)

            CGEventPost(kCGHIDEventTap, event)
            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.mouse_up error: {e}")
            return False

    async def mouse_move(self, x: int, y: int, duration: float = 0.0) -> bool:
        try:
            current_pos = await self.get_mouse_position()
            start_x, start_y = current_pos

            if duration <= 0:
                # Calculate human-like movement duration based on distance
                duration = calc_move_duration(x, y, start_x, start_y)

            if duration > 0:
                await self._perform_smooth_movement(
                    start_x, start_y, x, y, duration, kCGEventMouseMoved
                )
            else:
                # Fallback to instant movement (shouldn't happen)
                point = CGPointMake(x, y)
                event = CGEventCreateMouseEvent(self._event_source, kCGEventMouseMoved, point, 0)
                CGEventPost(kCGHIDEventTap, event)

            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.mouse_move error: {e}")
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
            await self.mouse_down(start_x, start_y, button)
            drag_event_type, button_num = self._get_button_event_info(button, "drag")
            await self._perform_smooth_movement(
                start_x, start_y, end_x, end_y, duration, drag_event_type, button_num
            )
            await self.mouse_up(end_x, end_y, button)
            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.drag error: {e}")
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
                delta_y = amount
                delta_x = 0
            elif direction == ScrollDirection.DOWN:
                delta_y = -amount
                delta_x = 0
            elif direction == ScrollDirection.LEFT:
                delta_x = amount
                delta_y = 0
            else:  # RIGHT
                delta_x = -amount
                delta_y = 0

            wheel_count = 2  # Number of axes
            event = CGEventCreateScrollWheelEvent(
                self._event_source,
                kCGScrollEventUnitLine,
                wheel_count,
                delta_y,
                delta_x,
            )

            CGEventPost(kCGHIDEventTap, event)
            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.scroll error: {e}")
            return False

    async def type_text(self, text: str, delay_ms: int = TYPING_DELAY_MS) -> bool:
        try:
            for char in text:
                key_code = self._char_to_keycode(char)
                if key_code is None:
                    logger.debug(f"No keycode for character: {char}")
                    continue

                down_event = CGEventCreateKeyboardEvent(self._event_source, key_code, True)

                # Handle Shift for uppercase letters and special characters
                if char.isupper() or char in '!@#$%^&*()_+{}|:"<>?':
                    CGEventSetFlags(down_event, NSShiftKeyMask)

                CGEventPost(kCGHIDEventTap, down_event)

                up_event = CGEventCreateKeyboardEvent(self._event_source, key_code, False)
                CGEventPost(kCGHIDEventTap, up_event)

                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)

            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.type_text error: {e}")
            return False

    async def key_press(self, key: str, modifiers: Optional[KeyModifier] = None) -> bool:
        try:
            # Check if key contains modifiers
            # Delimited by "+" (e.g., "ctrl+a", "cmd+tab")
            if "+" in key:
                parts = key.lower().split("+")
                actual_key = parts[-1]
                mod_parts = parts[:-1]

                # Build mod flags
                flags = 0
                for mod in mod_parts:
                    if mod in ["ctrl", "control"]:
                        flags |= NSControlKeyMask
                    elif mod in ["alt", "option"]:
                        flags |= NSAlternateKeyMask
                    elif mod in ["shift"]:
                        flags |= NSShiftKeyMask
                    elif mod in ["cmd", "command", "meta"]:
                        flags |= NSCommandKeyMask

                key_code = self._key_map.get(actual_key.lower())
            else:
                key_code = self._key_map.get(key.lower())

                # Build modifier flags from KeyModifier object
                flags = 0
                if modifiers:
                    if modifiers.ctrl:
                        flags |= NSControlKeyMask
                    if modifiers.alt:
                        flags |= NSAlternateKeyMask
                    if modifiers.shift:
                        flags |= NSShiftKeyMask
                    if modifiers.meta:
                        flags |= NSCommandKeyMask

            if key_code is None:
                logger.debug(f"Unknown key: {key}")
                return False

            down_event = CGEventCreateKeyboardEvent(self._event_source, key_code, True)
            if flags:
                CGEventSetFlags(down_event, flags)
            CGEventPost(kCGHIDEventTap, down_event)

            up_event = CGEventCreateKeyboardEvent(self._event_source, key_code, False)
            CGEventPost(kCGHIDEventTap, up_event)

            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.key_press error: {e}")
            return False

    async def key_down(self, key: str) -> bool:
        try:
            key_code = self._key_map.get(key.lower())
            if key_code is None:
                return False

            event = CGEventCreateKeyboardEvent(self._event_source, key_code, True)
            CGEventPost(kCGHIDEventTap, event)
            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.key_down error: {e}")
            return False

    async def key_up(self, key: str) -> bool:
        try:
            key_code = self._key_map.get(key.lower())
            if key_code is None:
                return False

            event = CGEventCreateKeyboardEvent(self._event_source, key_code, False)
            CGEventPost(kCGHIDEventTap, event)
            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.key_up error: {e}")
            return False

    async def hotkey(self, keys: List[str]) -> bool:
        try:
            pressed_keys = []
            flags = 0

            # Split list of keys into modifier flags and non-modifier keys
            for key in keys:
                key_lower = key.lower()
                if key_lower in self._modifier_map:
                    flags |= self._modifier_map[key_lower]
                else:
                    key_code = self._key_map.get(key.lower())
                    if key_code is not None:
                        pressed_keys.append(key_code)

            for key_code in pressed_keys:
                down_event = CGEventCreateKeyboardEvent(self._event_source, key_code, True)
                if flags:
                    CGEventSetFlags(down_event, flags)
                CGEventPost(kCGHIDEventTap, down_event)

            # Release non-modifier keys
            # macOS automatically handles clearing modifier flags on key up
            for key_code in reversed(pressed_keys):
                up_event = CGEventCreateKeyboardEvent(self._event_source, key_code, False)
                CGEventPost(kCGHIDEventTap, up_event)

            return True
        except Exception as e:
            cn = self.__class__.__name__
            logger.debug(f"{cn}.hotkey error: {e}")
            return False

    async def get_mouse_position(self) -> Tuple[int, int]:
        try:
            # Create a dummy event to get current mouse location
            event = CGEventCreate(None)
            location = CGEventGetLocation(event)
            return (int(location.x), int(location.y))
        except Exception:
            return (0, 0)

    async def _smooth_move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move cursor smoothly to target position with human-like motion."""
        if duration is None:
            current_pos = await self.get_mouse_position()
            duration = calc_move_duration(x, y, current_pos[0], current_pos[1])

        await self.mouse_move(x, y, duration=duration)

    async def _perform_smooth_movement(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float,
        event_type: int,
        button_num: int = 0,
    ) -> None:
        """Perform smooth interpolated movement from start to end position."""
        steps = max(int(duration * 60), 1)  # 60 FPS
        delay = duration / steps

        distance = calc_distance(start_x, start_y, end_x, end_y)
        easing_func = (
            pytweening.easeOutExpo
            if distance < SHORT_DISTANCE_THRESHOLD
            else pytweening.easeInOutSine
        )

        for i in range(steps + 1):
            progress = i / steps
            t = easing_func(progress)

            current_x = start_x + (end_x - start_x) * t
            current_y = start_y + (end_y - start_y) * t

            point = CGPointMake(current_x, current_y)
            event = CGEventCreateMouseEvent(self._event_source, event_type, point, button_num)
            CGEventPost(kCGHIDEventTap, event)

            if i < steps:
                await asyncio.sleep(delay)

    def _build_modifier_map(self) -> dict:
        """Build mapping of modifier names to flags."""
        return {
            "shift": NSShiftKeyMask,
            "ctrl": NSControlKeyMask,
            "control": NSControlKeyMask,
            "alt": NSAlternateKeyMask,
            "option": NSAlternateKeyMask,
            "cmd": NSCommandKeyMask,
            "command": NSCommandKeyMask,
            "meta": NSCommandKeyMask,
        }

    def _get_button_event_info(
        self, button: MouseButton, event_kind: Literal["down", "up", "drag"]
    ) -> Tuple[int, int]:
        """Get event type and button number for a mouse button.

        Args:
            button: The mouse button
            event_kind: One of 'down', 'up', or 'drag'

        Returns:
            Tuple of (event_type, button_number)
        """
        if button == MouseButton.LEFT:
            event_types = {
                "down": kCGEventLeftMouseDown,
                "up": kCGEventLeftMouseUp,
                "drag": kCGEventLeftMouseDragged,
            }
            button_num = kCGMouseButtonLeft
        elif button == MouseButton.RIGHT:
            event_types = {
                "down": kCGEventRightMouseDown,
                "up": kCGEventRightMouseUp,
                "drag": kCGEventRightMouseDragged,
            }
            button_num = kCGMouseButtonRight
        else:  # Middle button
            event_types = {
                "down": kCGEventOtherMouseDown,
                "up": kCGEventOtherMouseUp,
                "drag": kCGEventOtherMouseDragged,
            }
            button_num = kCGMouseButtonCenter

        return event_types[event_kind], button_num

    def _build_key_map(self) -> dict:
        """Build mapping of key names to macOS key codes."""
        return {
            # Letters
            "a": 0x00,
            "b": 0x0B,
            "c": 0x08,
            "d": 0x02,
            "e": 0x0E,
            "f": 0x03,
            "g": 0x05,
            "h": 0x04,
            "i": 0x22,
            "j": 0x26,
            "k": 0x28,
            "l": 0x25,
            "m": 0x2E,
            "n": 0x2D,
            "o": 0x1F,
            "p": 0x23,
            "q": 0x0C,
            "r": 0x0F,
            "s": 0x01,
            "t": 0x11,
            "u": 0x20,
            "v": 0x09,
            "w": 0x0D,
            "x": 0x07,
            "y": 0x10,
            "z": 0x06,
            # Numbers
            "0": 0x1D,
            "1": 0x12,
            "2": 0x13,
            "3": 0x14,
            "4": 0x15,
            "5": 0x17,
            "6": 0x16,
            "7": 0x1A,
            "8": 0x1C,
            "9": 0x19,
            # Function keys
            "f1": 0x7A,
            "f2": 0x78,
            "f3": 0x63,
            "f4": 0x76,
            "f5": 0x60,
            "f6": 0x61,
            "f7": 0x62,
            "f8": 0x64,
            "f9": 0x65,
            "f10": 0x6D,
            "f11": 0x67,
            "f12": 0x6F,
            # Special keys
            "return": 0x24,
            "enter": 0x24,
            "tab": 0x30,
            "space": 0x31,
            " ": 0x31,
            "delete": 0x33,
            "backspace": 0x33,
            "escape": 0x35,
            "esc": 0x35,
            "command": 0x37,
            "cmd": 0x37,
            "shift": 0x38,
            "capslock": 0x39,
            "option": 0x3A,
            "alt": 0x3A,
            "control": 0x3B,
            "ctrl": 0x3B,
            # Arrow keys
            "left": 0x7B,
            "right": 0x7C,
            "down": 0x7D,
            "up": 0x7E,
            # Punctuation
            "period": 0x2F,
            ".": 0x2F,
            "comma": 0x2B,
            ",": 0x2B,
            "slash": 0x2C,
            "/": 0x2C,
            "semicolon": 0x29,
            ";": 0x29,
            "quote": 0x27,
            "'": 0x27,
            "bracket_left": 0x21,
            "[": 0x21,
            "bracket_right": 0x1E,
            "]": 0x1E,
            "backslash": 0x2A,
            "\\": 0x2A,
            "minus": 0x1B,
            "-": 0x1B,
            "equal": 0x18,
            "=": 0x18,
            "grave": 0x32,
            "`": 0x32,
            # Navigation
            "home": 0x73,
            "end": 0x77,
            "pageup": 0x74,
            "pagedown": 0x79,
        }

    def _char_to_keycode(self, char: str) -> Optional[int]:
        """Convert a character to its key code."""
        # Handle basic ASCII characters
        char_lower = char.lower()
        if char_lower in self._key_map:
            return self._key_map[char_lower]

        # Map some special characters to their base keys
        special_chars = {
            "!": "1",
            "@": "2",
            "#": "3",
            "$": "4",
            "%": "5",
            "^": "6",
            "&": "7",
            "*": "8",
            "(": "9",
            ")": "0",
            "_": "-",
            "+": "=",
            "{": "[",
            "}": "]",
            "|": "\\",
            ":": ";",
            '"': "'",
            "<": ",",
            ">": ".",
            "?": "/",
            "~": "`",
        }

        if char in special_chars:
            base_char = special_chars[char]
            return self._key_map.get(base_char)

        return None
