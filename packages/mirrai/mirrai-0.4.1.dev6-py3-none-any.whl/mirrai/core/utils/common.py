import math
import platform
import random
import re
from typing import Optional, Tuple

from mirrai.core.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    MAX_MOVE_DURATION,
    MIN_MOVE_DURATION,
    PIXELS_PER_SECOND,
)


def format_bytes(size_bytes: int) -> str:
    """Format bytes into human readable string."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_primary_display_size() -> Tuple[int, int]:
    """Get the primary display size for the current platform."""
    if IS_WINDOWS:
        import win32api  # type: ignore

        return (
            win32api.GetSystemMetrics(0),  # SM_CXSCREEN
            win32api.GetSystemMetrics(1),  # SM_CYSCREEN
        )
    elif IS_MACOS:
        # Use Quartz to get display size
        from Quartz.CoreGraphics import CGDisplayBounds  # type: ignore
        from Quartz.CoreGraphics import CGMainDisplayID  # type: ignore

        main_display = CGMainDisplayID()
        bounds = CGDisplayBounds(main_display)
        return (int(bounds.size.width), int(bounds.size.height))
    elif IS_LINUX:
        # Try X11 first
        try:
            from Xlib import display  # type: ignore

            d = display.Display()
            s = d.screen()
            width = s.width_in_pixels
            height = s.height_in_pixels
            d.close()
            return (width, height)
        except Exception:
            pass

        # If we didn't return, Xlib failed. Fallback to xrandr.
        try:
            import subprocess

            result = subprocess.run(
                ["xrandr", "--current"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Parse primary display from xrandr output
                for line in result.stdout.split("\n"):
                    if " primary " in line or (line.startswith(" ") and " connected" in line):
                        # Extract resolution like "1920x1080"

                        match = re.search(r"(\d+)x(\d+)", line)
                        if match:
                            return (int(match.group(1)), int(match.group(2)))
        except Exception:
            pass

        # Shouldn't happen in practice, assume common resolution for now
        return (1920, 1080)
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported")


def calc_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calc_move_duration(
    target_x: int,
    target_y: int,
    current_x: Optional[int] = None,
    current_y: Optional[int] = None,
) -> float:
    """Calculate human-like movement duration based on distance."""
    if current_x is None or current_y is None:
        return MIN_MOVE_DURATION

    distance = calc_distance(current_x, current_y, target_x, target_y)
    base_duration = distance / PIXELS_PER_SECOND

    # ±10% variation for more human-like movement
    variation = random.uniform(0.9, 1.1)
    duration = base_duration * variation

    return max(MIN_MOVE_DURATION, min(duration, MAX_MOVE_DURATION))


def calc_levenshtein_dist(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        # Optimization: s1 should be longer string
        return calc_levenshtein_dist(s2, s1)

    if len(s2) == 0:
        # If s2 (shorter string) is empty, s1 is always the edit distance (n deletions from s1)
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
