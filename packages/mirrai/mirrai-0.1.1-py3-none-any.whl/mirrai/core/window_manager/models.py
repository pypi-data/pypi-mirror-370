"""Types and models for window management."""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from pydantic import BaseModel, computed_field


class Rect(BaseModel):
    """Rectangle with named coordinates."""

    left: int
    top: int
    right: int
    bottom: int

    @computed_field
    @property
    def width(self) -> int:
        """Calculate width from coordinates."""
        return self.right - self.left

    @computed_field
    @property
    def height(self) -> int:
        """Calculate height from coordinates."""
        return self.bottom - self.top

    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to tuple format (left, top, right, bottom)."""
        return (self.left, self.top, self.right, self.bottom)

    @classmethod
    def from_tuple(cls, rect_tuple: Tuple[int, int, int, int]) -> "Rect":
        """Create from tuple format (left, top, right, bottom)."""
        return cls(left=rect_tuple[0], top=rect_tuple[1], right=rect_tuple[2], bottom=rect_tuple[3])


class WindowInfo(BaseModel):
    """Platform-agnostic window information."""

    window_id: int  # HWND on Windows, CGWindowID on macOS
    title: str
    class_name: str
    pid: int
    is_visible: bool
    rect: Rect

    @computed_field
    @property
    def width(self) -> int:
        return self.rect.width

    @computed_field
    @property
    def height(self) -> int:
        return self.rect.height


class WindowSpecType(Enum):
    """Types of window specifications."""

    TITLE = "title"
    ID = "id"
    PROCESS = "process"
    PID = "pid"


@dataclass
class WindowSpec:
    """Parsed window specification."""

    type: WindowSpecType
    value: str

    @classmethod
    def parse(cls, spec: str) -> "WindowSpec":
        """Parse a window specification string.

        Formats:
        - "title:Window Title" or "Window Title" (default)
        - "id:12345" (window ID/HWND)
        - "process:notepad" (process name without extension)
        - "pid:1234" (process ID)

        Args:
            spec: Window specification string

        Returns:
            Parsed WindowSpec object
        """
        if not spec:
            raise ValueError("Window specification cannot be empty")

        # Check for prefix
        if ":" in spec:
            prefix, value = spec.split(":", 1)
            prefix = prefix.lower().strip()
            value = value.strip()

            if not value:
                raise ValueError(f"Empty value for prefix '{prefix}'")

            if prefix == "title":
                return cls(WindowSpecType.TITLE, value)
            elif prefix == "id":
                # Validate that it's a number
                try:
                    int(value)
                except ValueError:
                    raise ValueError(f"Window ID must be a number, got: {value}")
                return cls(WindowSpecType.ID, value)
            elif prefix == "process":
                # Remove .exe extension if present (for Windows compatibility)
                if value.lower().endswith(".exe"):
                    value = value[:-4]
                return cls(WindowSpecType.PROCESS, value)
            elif prefix == "pid":
                # Validate that it's a number
                try:
                    int(value)
                except ValueError:
                    raise ValueError(f"Process ID must be a number, got: {value}")
                return cls(WindowSpecType.PID, value)
            else:
                # Unknown prefix, treat entire string as title
                return cls(WindowSpecType.TITLE, spec)

        # No prefix, default to title
        return cls(WindowSpecType.TITLE, spec)
