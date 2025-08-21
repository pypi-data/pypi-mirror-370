from mirrai.core.utils.patterns import PlatformFactory
from mirrai.core.window_manager.base import WindowManager


class WindowManagerFactory(PlatformFactory[WindowManager]):
    """Factory class for creating platform-specific WindowManager instances."""

    @classmethod
    def _create_windows(cls) -> WindowManager:
        """Create Windows WindowManager implementation."""
        from .windows import WindowsWindowManager

        return WindowsWindowManager()

    @classmethod
    def _create_linux(cls) -> WindowManager:
        """Create Linux WindowManager implementation."""
        if cls._is_i3_running():
            # i3 support:
            # for me and the 3 people worldwide who would be using i3 and an agent like this simultaneously
            from .linux_i3 import I3WindowManager

            return I3WindowManager()
        else:
            from .linux import LinuxWindowManager

            return LinuxWindowManager()

    @classmethod
    def _create_macos(cls) -> WindowManager:
        """Create macOS WindowManager implementation."""
        from .macos import MacOSWindowManager

        return MacOSWindowManager()

    @classmethod
    def _is_i3_running(cls) -> bool:
        """Check if i3 window manager is running."""
        try:
            import subprocess

            result = subprocess.run(
                ["i3-msg", "-t", "get_version"], capture_output=True, timeout=0.5
            )
            return result.returncode == 0
        except:
            return False
