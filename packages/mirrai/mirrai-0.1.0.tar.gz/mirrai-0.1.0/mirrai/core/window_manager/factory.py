from mirrai.core.utils import PlatformFactory
from mirrai.core.window_manager.base import WindowManager


class WindowManagerFactory(PlatformFactory[WindowManager]):
    """Factory class for creating platform-specific WindowManager instances."""

    @classmethod
    def _create_windows(cls) -> WindowManager:
        """Create Windows WindowManager implementation."""
        from .windows import WindowsWindowManager

        return WindowsWindowManager()
