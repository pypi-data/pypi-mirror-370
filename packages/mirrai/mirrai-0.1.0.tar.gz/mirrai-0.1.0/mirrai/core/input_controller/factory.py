from mirrai.core.input_controller.base import InputController
from mirrai.core.utils import PlatformFactory


class InputControllerFactory(PlatformFactory[InputController]):
    """Factory class for creating platform-specific InputController instances."""

    @classmethod
    def _create_windows(cls) -> InputController:
        """Create Windows InputController implementation."""
        from .windows import WindowsInputController

        return WindowsInputController()
