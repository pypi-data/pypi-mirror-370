"""Abstract base class for window management."""

from abc import ABC, abstractmethod
from typing import List, Optional

import psutil

from mirrai.core.window_manager.models import Rect, WindowInfo, WindowSpec, WindowSpecType


class WindowManager(ABC):
    """Abstract base class for window management across platforms."""

    @abstractmethod
    def list_windows(self, filter_visible: bool = True) -> List[WindowInfo]:
        """
        List all windows.

        Args:
            filter_visible: If True, only return visible windows with titles

        Returns:
            List of WindowInfo objects
        """
        pass

    def find_window_by_title(
        self,
        title: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> Optional[WindowInfo]:
        """
        Find a window by title or class name.

        Args:
            title: Window title to search for (partial match, case-insensitive)
            class_name: Window class name to search for (exact match)

        Returns:
            First matching WindowInfo or None if not found
        """
        windows = self.list_windows()
        for window in windows:
            if title and title.lower() not in window.title.lower():
                continue
            if class_name and class_name != window.class_name:
                continue
            return window
        return None

    def find_window_by_pid(self, pid: int) -> Optional[WindowInfo]:
        """
        Find a window by process ID.

        Args:
            pid: Process ID to search for

        Returns:
            First matching WindowInfo or None if not found
        """
        windows = self.list_windows()
        for window in windows:
            if window.pid == pid:
                return window
        return None

    @abstractmethod
    def find_window_by_id(self, window_id: int) -> Optional[WindowInfo]:
        """
        Find a window by its ID (HWND on Windows).

        Args:
            window_id: Window identifier

        Returns:
            WindowInfo if found, None otherwise
        """
        pass

    def find_window(self, spec: str) -> Optional[WindowInfo]:
        """
        Find a window using a flexible specification string.

        Args:
            spec: Window specification (e.g., "title:Notepad", "id:12345", "process:chrome")

        Returns:
            First matching WindowInfo or None if not found
        """
        parsed = WindowSpec.parse(spec)

        if parsed.type == WindowSpecType.TITLE:
            return self.find_window_by_title(title=parsed.value)
        elif parsed.type == WindowSpecType.ID:
            return self.find_window_by_id(int(parsed.value))
        elif parsed.type == WindowSpecType.PROCESS:
            # Find by process name (implementation specific)
            return self.find_window_by_process(parsed.value)
        elif parsed.type == WindowSpecType.PID:
            return self.find_window_by_pid(int(parsed.value))

        return None

    def find_window_by_process(self, process_name: str) -> Optional[WindowInfo]:
        """
        Find a window by process name (without extension).

        Args:
            process_name: Process name (e.g., "notepad", "chrome")

        Returns:
            First matching WindowInfo or None if not found
        """
        windows = self.list_windows()
        process_name_lower = process_name.lower()

        for window in windows:
            try:
                # Get process info
                process = psutil.Process(window.pid)
                proc_name = process.name()

                # Remove .exe extension if present
                if proc_name.lower().endswith(".exe"):
                    proc_name = proc_name[:-4]

                # Check if process name matches
                if proc_name.lower() == process_name_lower:
                    return window
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return None

    @abstractmethod
    def get_focused_window(self) -> Optional[int]:
        """
        Get the currently focused window ID.

        Returns:
            Window ID of the currently focused window, or None if no window is focused
        """
        pass

    @abstractmethod
    def focus_window(self, window_id: int) -> bool:
        """
        Bring a window to the foreground and give it focus.

        Args:
            window_id: Window identifier (HWND on Windows)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_window_rect(self, window_id: int) -> Optional[Rect]:
        """
        Get window position and size.

        Args:
            window_id: Window identifier (HWND on Windows)

        Returns:
            Rect with window coordinates or None if not found
        """
        pass

    @abstractmethod
    def get_client_rect(self, window_id: int) -> Optional[Rect]:
        """
        Get client area position and size (content area excluding borders/titlebar).

        Args:
            window_id: Window identifier (HWND on Windows)

        Returns:
            Rect with client area coordinates or None if not found
        """
        pass
