import os
import subprocess
from enum import Enum

from rich.panel import Panel
from rich.text import Text

from mirrai.core.constants import IS_MACOS


class PermissionType(Enum):
    ACCESSIBILITY = "accessibility"
    SCREEN_RECORDING = "screen_recording"


class MacOSPermissions:
    """Handle macOS permission checks and user prompts."""

    @staticmethod
    def check_accessibility() -> bool:
        """Check if the application has accessibility permissions."""
        if not IS_MACOS:
            return True

        try:
            from ApplicationServices import AXIsProcessTrusted  # type: ignore

            return AXIsProcessTrusted()
        except Exception:
            # Fallback assumes we have permission
            # Worst that can happen is that it doesn't work
            return True

    @staticmethod
    def check_screen_recording() -> bool:
        """Check if the application has screen recording permissions."""
        if not IS_MACOS:
            return True

        try:
            import Quartz  # type: ignore

            window_list = Quartz.CGWindowListCopyWindowInfo(  # type: ignore
                Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,  # type: ignore
                Quartz.kCGNullWindowID,  # type: ignore
            )

            # Check if we can actually capture screen content:
            # I couldn't find a direct way to do this via any first party APIs.
            # If CGWindowListCreateImage returns None, we probably don't have permission.
            if window_list and len(window_list) > 0:
                window_id = window_list[0].get("kCGWindowNumber", 0)
                if window_id:
                    test_img = Quartz.CGWindowListCreateImage(  # type: ignore
                        Quartz.CGRectNull,  # type: ignore
                        Quartz.kCGWindowListOptionIncludingWindow,  # type: ignore
                        window_id,
                        Quartz.kCGWindowImageDefault,  # type: ignore
                    )
                    return test_img is not None
            return True
        except Exception:
            # Fallback assumes we have permission
            # Worst that can happen is that it doesn't work
            return True

    @staticmethod
    def request_accessibility() -> None:
        """Request accessibility permissions from the user."""
        if not IS_MACOS:
            return

        try:
            from ApplicationServices import AXIsProcessTrustedWithOptions  # type: ignore
            from CoreFoundation import kCFBooleanTrue  # type: ignore

            # This will show the system dialog
            options = {"AXTrustedCheckOptionPrompt": kCFBooleanTrue}
            AXIsProcessTrustedWithOptions(options)
        except Exception:
            pass

    @staticmethod
    def request_screen_recording() -> None:
        """
        Request screen recording permissions from the user.

        Note: Unlike accessibility, it seems like there is no direct API  to trigger the screen recording permission dialog.
        We try to use a URL scheme approach instead.
        """
        if not IS_MACOS:
            return

        try:
            # Open System Preferences directly to Screen Recording settings
            subprocess.run(
                [
                    "open",
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture",
                ],
                check=False,
            )
        except Exception:
            # Fallback: try to open general Privacy & Security settings
            try:
                subprocess.run(
                    ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy"],
                    check=False,
                )
            except Exception:
                pass

    @staticmethod
    def show_permission_alert(permission_type: PermissionType) -> None:
        """Show a permission alert to the user and exit."""
        from mirrai.core.logger import logger

        alert_text = Text()

        if permission_type == PermissionType.ACCESSIBILITY:
            alert_text.append("Accessibility Permissions Required\n\n", style="bold yellow")
            alert_text.append(
                "mirrai needs accessibility permissions to control your mouse and keyboard.\n\n"
            )
            alert_text.append("Opening system dialog to request permission...\n\n", style="italic")
            alert_text.append("Please follow these steps:\n", style="bold")
            alert_text.append("1. Click 'Open System Settings' in the dialog\n")
            alert_text.append("2. Find your terminal app in the list\n")
            alert_text.append("3. Toggle the switch to enable it\n")
            alert_text.append("4. Run the command again", style="bold cyan")

        elif permission_type == PermissionType.SCREEN_RECORDING:
            alert_text.append("Screen Recording Permission Required\n\n", style="bold yellow")
            alert_text.append(
                "mirrai needs screen recording permissions to capture screenshots.\n\n"
            )
            alert_text.append("Opening System Settings to Screen Recording...\n\n", style="italic")
            alert_text.append("Please follow these steps:\n", style="bold")
            alert_text.append(
                "1. System Settings will open to Privacy & Security → Screen Recording\n"
            )
            alert_text.append("2. Find your terminal app in the list\n")
            alert_text.append("3. Toggle the switch to enable it\n")
            alert_text.append("4. You may need to restart your terminal\n")
            alert_text.append("5. Run the command again", style="bold cyan")

        panel = Panel(
            alert_text,
            title="[bold red]PERMISSION REQUIRED[/bold red]",
            border_style="red",
            padding=(1, 2),
        )

        logger.print(panel)
        os._exit(0)

    @classmethod
    def ensure_accessibility(cls) -> None:
        """
        Ensure accessibility permissions are granted.
        Shows alert and exits if not granted.
        """
        if not cls.check_accessibility():
            cls.request_accessibility()
            cls.show_permission_alert(PermissionType.ACCESSIBILITY)

    @classmethod
    def ensure_screen_recording(cls) -> None:
        """
        Ensure screen recording permissions are granted.
        Shows alert, opens System Preferences, and exits if not granted.
        """
        if not cls.check_screen_recording():
            cls.request_screen_recording()
            cls.show_permission_alert(PermissionType.SCREEN_RECORDING)
