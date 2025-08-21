from mirrai.core.input_controller.base import InputController
from mirrai.core.utils.patterns import PlatformFactory


class InputControllerFactory(PlatformFactory[InputController]):
    """Factory class for creating platform-specific InputController instances."""

    @classmethod
    def _create_windows(cls) -> InputController:
        """Create Windows InputController implementation."""
        from .windows import WindowsInputController

        return WindowsInputController()

    @classmethod
    def _create_linux(cls) -> InputController:
        """
        Create Linux InputController implementation.
        X11 only; Wayland not yet supported.
        """
        from .linux import LinuxInputController

        return LinuxInputController()

    @classmethod
    def _create_macos(cls) -> InputController:
        """Create macOS InputController implementation."""
        from .macos import MacOSInputController

        return MacOSInputController()
