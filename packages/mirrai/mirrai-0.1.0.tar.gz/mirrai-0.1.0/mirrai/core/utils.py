import math
import platform
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar

T = TypeVar("T")


class Singleton(type):
    """Metaclass for creating singleton classes."""

    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset_instance(cls) -> None:
        """Reset the singleton instance."""
        if cls in cls._instances:
            del cls._instances[cls]


class PlatformFactory(Generic[T], ABC):
    """Base class for platform-specific factory implementations.

    This provides a common pattern for creating singleton instances
    of platform-specific implementations (Windows, macOS, Linux).
    """

    _instance: Optional[T] = None

    @classmethod
    @abstractmethod
    def _create_windows(cls) -> T:
        """Create Windows implementation. Must be overridden by subclasses."""
        pass

    @classmethod
    def _create_macos(cls) -> T:
        """Create macOS implementation. Override if macOS is supported."""
        raise NotImplementedError(f"macOS {cls.__name__} not yet implemented")

    @classmethod
    def _create_linux(cls) -> T:
        """Create Linux implementation. Override if Linux is supported."""
        raise NotImplementedError(f"Linux {cls.__name__} not yet implemented")

    @classmethod
    def get(cls) -> T:
        """Get the platform-specific instance.

        Creates a singleton instance on first call and returns the same
        instance on subsequent calls.

        Returns:
            Platform-specific implementation instance

        Raises:
            NotImplementedError: If the current platform is not supported
        """
        if cls._instance is None:
            system = platform.system()

            if system == "Windows":
                cls._instance = cls._create_windows()
            elif system == "Darwin":  # macOS
                cls._instance = cls._create_macos()
            elif system == "Linux":
                cls._instance = cls._create_linux()
            else:
                raise NotImplementedError(f"Platform {system} is not supported")

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the cached instance. Useful for testing."""
        cls._instance = None


def format_bytes(size_bytes: int) -> str:
    """Format bytes into human readable size.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human readable size string (e.g., "1.5 MB", "256 KB")
    """
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_primary_display_size() -> Tuple[int, int]:
    system = platform.system()

    if system == "Windows":
        import win32api

        return (
            win32api.GetSystemMetrics(0),  # SM_CXSCREEN
            win32api.GetSystemMetrics(1),  # SM_CYSCREEN
        )
    elif system == "Darwin":  # macOS
        # Quartz/AppKit
        raise NotImplementedError("macOS display size not yet implemented")
    elif system == "Linux":
        # X11/Wayland
        raise NotImplementedError("Linux display size not yet implemented")
    else:
        raise NotImplementedError(f"Platform {system} is not supported")


# Minimum duration for any movement
MIN_MOVE_DURATION = 0.2

# Maximum duration for longer movements
MAX_MOVE_DURATION = 0.6

# Base movement speed
PIXELS_PER_SECOND = 1500

# Threshold for short vs long movements (in pixels)
SHORT_DISTANCE_THRESHOLD = 200


def calc_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points.

    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates

    Returns:
        Distance in pixels
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calc_move_duration(
    target_x: int,
    target_y: int,
    current_x: Optional[int] = None,
    current_y: Optional[int] = None,
) -> float:
    """Calculate human-like movement duration based on distance.

    Args:
        target_x, target_y: Target coordinates
        current_x, current_y: Current coordinates (if None, returns minimum duration)

    Returns:
        Duration in seconds for the movement
    """
    if current_x is None or current_y is None:
        return MIN_MOVE_DURATION

    distance = calc_distance(current_x, current_y, target_x, target_y)
    base_duration = distance / PIXELS_PER_SECOND

    # ±10% variation for more human-like movement
    variation = random.uniform(0.9, 1.1)
    duration = base_duration * variation

    return max(MIN_MOVE_DURATION, min(duration, MAX_MOVE_DURATION))
