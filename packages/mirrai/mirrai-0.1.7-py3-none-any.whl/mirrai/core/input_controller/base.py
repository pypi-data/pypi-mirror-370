from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class MouseButton(Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ScrollDirection(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class KeyModifier:
    ctrl: bool = False
    alt: bool = False
    shift: bool = False
    meta: bool = False  # Windows key or Command key


class InputController(ABC):

    @abstractmethod
    async def click(
        self,
        x: int,
        y: int,
        button: MouseButton = MouseButton.LEFT,
        double_click: bool = False,
        triple_click: bool = False,
    ) -> bool:
        """
        Click at the specified coordinates.

        Args:
            x: X coordinate (screen coordinate)
            y: Y coordinate (screen coordinate)
            button: Which mouse button to click
            double_click: Perform a double-click
            triple_click: Perform a triple-click

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def mouse_down(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        """
        Press and hold mouse button at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Which mouse button to press

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def mouse_up(self, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
        """
        Release mouse button at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Which mouse button to release

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def mouse_move(self, x: int, y: int, duration: float = 0.0) -> bool:
        """
        Move mouse cursor to coordinates.

        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Time in seconds to perform the movement (0 for instant)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        button: MouseButton = MouseButton.LEFT,
        duration: float = 0.5,
    ) -> bool:
        """
        Drag from start to end coordinates.

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            button: Which mouse button to hold during drag
            duration: Time in seconds to perform the drag

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def scroll(
        self,
        direction: ScrollDirection,
        amount: int = 3,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> bool:
        """
        Scroll in the specified direction.

        Args:
            direction: Direction to scroll
            amount: Number of scroll units
            x: Optional X coordinate to scroll at (None = current position)
            y: Optional Y coordinate to scroll at (None = current position)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def type_text(self, text: str, delay_ms: int = 12) -> bool:
        """
        Type text as if typed on keyboard.

        Args:
            text: Text to type
            delay_ms: Delay between keystrokes in milliseconds

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def key_press(self, key: str, modifiers: Optional[KeyModifier] = None) -> bool:
        """
        Press a single key or key combination.

        Args:
            key: Key to press (e.g., "a", "Return", "F1", "space")
            modifiers: Optional key modifiers (Ctrl, Alt, Shift, Meta)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def key_down(self, key: str) -> bool:
        """
        Press and hold a key.

        Args:
            key: Key to press and hold

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def key_up(self, key: str) -> bool:
        """
        Release a held key.

        Args:
            key: Key to release

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def hotkey(self, keys: List[str]) -> bool:
        """
        Press a hotkey combination (e.g., Ctrl+S, Cmd+Tab).

        Args:
            keys: List of keys to press simultaneously (e.g., ["ctrl", "s"])

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position.

        Returns:
            Tuple of (x, y) coordinates
        """
        pass
