from typing import List, Optional

from mirrai.core.constants import IS_MACOS

if IS_MACOS:
    # Core Graphics: https://developer.apple.com/documentation/coregraphics
    # AppKit: https://developer.apple.com/documentation/appkit

    # PyObjC provides Python bindings for macOS frameworks but lacks complete type stubs.
    # We need to ignore basedpyright errors for these.

    from AppKit import (  # type: ignore
        NSApplicationActivateIgnoringOtherApps,  # type: ignore
        NSRunningApplication,  # type: ignore
        NSWorkspace,  # type: ignore
    )
    from Quartz.CoreGraphics import CGWindowListCopyWindowInfo  # type: ignore
    from Quartz.CoreGraphics import kCGNullWindowID  # type: ignore
    from Quartz.CoreGraphics import kCGWindowBounds  # type: ignore
    from Quartz.CoreGraphics import kCGWindowIsOnscreen  # type: ignore
    from Quartz.CoreGraphics import (  # type: ignore
        kCGWindowListExcludeDesktopElements,  # type: ignore
    )
    from Quartz.CoreGraphics import kCGWindowListOptionAll  # type: ignore
    from Quartz.CoreGraphics import kCGWindowListOptionOnScreenOnly  # type: ignore
    from Quartz.CoreGraphics import kCGWindowName  # type: ignore
    from Quartz.CoreGraphics import kCGWindowNumber  # type: ignore
    from Quartz.CoreGraphics import kCGWindowOwnerName  # type: ignore
    from Quartz.CoreGraphics import kCGWindowOwnerPID  # type: ignore

from mirrai.core.logger import logger
from mirrai.core.window_manager.base import WindowManager
from mirrai.core.window_manager.models import Rect, WindowInfo


class MacOSWindowManager(WindowManager):
    """macOS implementation of WindowManager using Quartz and AppKit."""

    def __init__(self):
        self._workspace = NSWorkspace.sharedWorkspace()

    def get_focused_window(self) -> Optional[int]:
        try:
            # Get the active application
            active_app = self._workspace.activeApplication()
            if not active_app:
                return None

            pid = active_app.get("NSApplicationProcessIdentifier")
            if not pid:
                return None

            # Get windows for this PID and find the frontmost one
            windows = self._get_windows_for_pid(pid)
            if windows:
                # The first window in the list is typically the frontmost
                return windows[0].window_id

            return None
        except Exception as e:
            logger.debug(f"Error getting focused window: {e}")
            return None

    def find_window_by_id(self, window_id: int) -> Optional[WindowInfo]:
        try:
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionAll | kCGWindowListExcludeDesktopElements,  # type: ignore
                kCGNullWindowID,
            )

            if not window_list:
                return None

            # Find the window with matching ID
            for window_dict in window_list:
                if window_dict.get(kCGWindowNumber) == window_id:
                    return self._parse_window_dict(window_dict)

            return None
        except Exception as e:
            logger.debug(f"Error finding window by ID {window_id}: {e}")
            return None

    def list_windows(self, filter_visible: bool = True) -> List[WindowInfo]:
        windows = []

        try:
            # Choose options based on filter_visible
            options = kCGWindowListOptionOnScreenOnly if filter_visible else kCGWindowListOptionAll
            options |= kCGWindowListExcludeDesktopElements  # type: ignore[operator]

            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

            if not window_list:
                return windows

            for window_dict in window_list:
                # Parse window info
                window_info = self._parse_window_dict(window_dict)

                if window_info:
                    # Apply additional filtering if needed
                    if filter_visible and not window_info.title:
                        continue

                    windows.append(window_info)

        except Exception as e:
            logger.debug(f"Error listing windows: {e}")

        return windows

    def focus_window(self, window_id: int) -> bool:
        try:
            window_info = self.find_window_by_id(window_id)
            if not window_info:
                return False

            # Get the application for this PID
            apps = (
                NSRunningApplication.runningApplicationsWithProcessIdentifier_(window_info.pid)
                if hasattr(NSRunningApplication, "runningApplicationsWithProcessIdentifier_")
                else []
            )

            # Alternative method if the above doesn't work
            if not apps:
                # Try getting all running applications and filter by PID
                all_apps = self._workspace.runningApplications()
                apps = [app for app in all_apps if app.processIdentifier() == window_info.pid]

            if not apps:
                return False

            app = apps[0]

            # Activate brings to front
            return app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        except Exception as e:
            logger.debug(f"Error focusing window {window_id}: {e}")
            return False

    def get_window_rect(self, window_id: int) -> Optional[Rect]:
        try:
            window_info = self.find_window_by_id(window_id)
            if window_info:
                return window_info.rect
            return None
        except Exception:
            return None

    def get_client_rect(self, window_id: int) -> Optional[Rect]:
        """Get client area position and size."""
        try:
            rect = self.get_window_rect(window_id)
            if not rect:
                return None

            # On macOS, the window bounds from CGWindowListCopyWindowInfo should already represent the content area.
            return rect
        except Exception:
            return None

    def _parse_window_dict(self, window_dict: dict) -> Optional[WindowInfo]:
        """Parse a window dictionary from Quartz into WindowInfo."""
        try:
            window_id = window_dict.get(kCGWindowNumber)
            if window_id is None:
                return None

            title = window_dict.get(kCGWindowName, "")
            owner_name = window_dict.get(kCGWindowOwnerName, "")
            pid = window_dict.get(kCGWindowOwnerPID, 0)

            if not title and owner_name:
                # Use owner name as title
                title = owner_name

            bounds_dict = window_dict.get(kCGWindowBounds)
            if not bounds_dict:
                return None

            x = int(bounds_dict.get("X", 0))
            y = int(bounds_dict.get("Y", 0))
            width = int(bounds_dict.get("Width", 0))
            height = int(bounds_dict.get("Height", 0))

            is_visible = window_dict.get(kCGWindowIsOnscreen, False)

            return WindowInfo(
                window_id=int(window_id),
                title=title,
                class_name=owner_name or "",
                pid=int(pid),
                is_visible=bool(is_visible),
                rect=Rect(left=x, top=y, right=x + width, bottom=y + height),
            )
        except Exception as e:
            logger.debug(f"Error parsing window dict: {e}")
            return None

    def _get_windows_for_pid(self, pid: int) -> List[WindowInfo]:
        """Get all windows for a specific process ID."""
        windows = []

        try:
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionAll | kCGWindowListExcludeDesktopElements,  # type: ignore[operator]
                kCGNullWindowID,
            )

            if not window_list:
                return windows

            for window_dict in window_list:
                window_pid = window_dict.get(kCGWindowOwnerPID)
                if window_pid == pid:
                    window_info = self._parse_window_dict(window_dict)
                    if window_info:
                        windows.append(window_info)
        except Exception as e:
            logger.debug(f"Error getting windows for PID {pid}: {e}")

        return windows
