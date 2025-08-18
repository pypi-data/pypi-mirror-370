from mirrai.core.screen_capture.base import ScreenCapture
from mirrai.core.utils import PlatformFactory


class ScreenCaptureFactory(PlatformFactory[ScreenCapture]):
    """Factory class for creating platform-specific ScreenCapture instances."""

    @classmethod
    def _create_windows(cls) -> ScreenCapture:
        """Create Windows ScreenCapture implementation."""
        from .windows import WindowsScreenCapture

        return WindowsScreenCapture()
