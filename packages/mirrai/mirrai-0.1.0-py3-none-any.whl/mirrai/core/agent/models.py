from typing import Optional

from anthropic.types.beta import BetaToolComputerUse20250124Param
from pydantic import BaseModel, computed_field

from mirrai.core.utils import get_primary_display_size
from mirrai.core.window_manager.models import Rect, WindowInfo

# NOTE: Higher screen resolutions result in lower accuracy in all VLMs
# We downscale high resolutions when sending to the model,
# When a tool is called, we upscale coordinate positions (relative to the real screen size) to improve  results
# This should probably be A/B tested, this was just intuition
MAX_WIDTH = 1280
MAX_HEIGHT = 800

DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_ITERATIONS = 50


class WindowSetup(BaseModel):
    """Configuration for window targeting mode."""

    window: Optional[WindowInfo] = None
    rect: Optional[Rect] = None

    @computed_field
    @property
    def is_window_mode(self) -> bool:
        """Check if we're in window targeting mode."""
        return self.window is not None and self.rect is not None

    @computed_field
    @property
    def offset_x(self) -> int:
        """Get the X offset for window-relative coordinates."""
        return self.rect.left if self.rect else 0

    @computed_field
    @property
    def offset_y(self) -> int:
        """Get the Y offset for window-relative coordinates."""
        return self.rect.top if self.rect else 0


class DisplayConfig(BaseModel):
    """Configuration for display scaling between agent and actual screen."""

    # Real screen resolution
    display_width: int
    display_height: int

    # Resolution we tell the agent (potentially scaled down)
    display_width_scaled: int
    display_height_scaled: int

    # Scale factor between native resolution and agent.
    # If the screen (or window) is <= 1280x800, this will just be 1.
    scale_factor: float

    @classmethod
    def from_screen(
        cls, width: Optional[int] = None, height: Optional[int] = None
    ) -> "DisplayConfig":
        """Create config from screen or window dimensions.

        Args:
            width: Explicit width (e.g., for a window). If None, uses full screen.
            height: Explicit height (e.g., for a window). If None, uses full screen.
        """
        # Get actual dimensions
        if width is None or height is None:
            display_width, display_height = get_primary_display_size()
        else:
            display_width, display_height = width, height

        assert (
            display_width > 0 and display_height > 0
        ), f"Invalid display dimensions: {display_width}x{display_height}"

        if display_width <= MAX_WIDTH and display_height <= MAX_HEIGHT:
            scale_factor = 1.0
        else:
            scale_factor = min(MAX_WIDTH / display_width, MAX_HEIGHT / display_height)
            if scale_factor <= 0:
                scale_factor = 1.0

        return cls(
            display_width=display_width,
            display_height=display_height,
            display_width_scaled=int(display_width * scale_factor),
            display_height_scaled=int(display_height * scale_factor),
            scale_factor=scale_factor,
        )

    def to_computer_tool(self) -> BetaToolComputerUse20250124Param:
        """Convert to Anthropic tool definition for the API."""
        return BetaToolComputerUse20250124Param(
            type="computer_20250124",
            name="computer",
            display_width_px=self.display_width_scaled,
            display_height_px=self.display_height_scaled,
            display_number=1,
        )
