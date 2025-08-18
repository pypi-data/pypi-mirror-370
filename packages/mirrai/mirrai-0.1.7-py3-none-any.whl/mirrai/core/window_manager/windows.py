from typing import List, Optional

import win32con
import win32gui
import win32process

from mirrai.core.window_manager.base import WindowManager
from mirrai.core.window_manager.models import Rect, WindowInfo


class WindowsWindowManager(WindowManager):
    """Windows implementation of WindowManager using pywin32."""

    def get_focused_window(self) -> Optional[int]:
        try:
            hwnd = win32gui.GetForegroundWindow()
            return hwnd if hwnd else None
        except Exception:
            return None

    def find_window_by_id(self, window_id: int) -> Optional[WindowInfo]:
        # note: on windows, this is a window handle (HWND)
        # https://learn.microsoft.com/en-us/windows/apps/develop/ui-input/retrieve-hwnd
        try:
            if not win32gui.IsWindow(window_id):
                return None

            title = win32gui.GetWindowText(window_id)
            class_name = win32gui.GetClassName(window_id) or ""
            _, pid = win32process.GetWindowThreadProcessId(window_id)
            rect = win32gui.GetWindowRect(window_id)

            return WindowInfo(
                window_id=window_id,
                title=title,
                class_name=class_name,
                pid=pid,
                is_visible=bool(win32gui.IsWindowVisible(window_id)),
                rect=Rect(
                    left=rect[0],
                    top=rect[1],
                    right=rect[2],
                    bottom=rect[3],
                ),
            )
        except Exception:
            return None

    def list_windows(self, filter_visible: bool = True) -> List[WindowInfo]:
        windows = []

        def enum_callback(hwnd, _):
            try:
                if filter_visible and not win32gui.IsWindowVisible(hwnd):
                    return True

                title = win32gui.GetWindowText(hwnd)

                if filter_visible and not title:
                    return True

                class_name = win32gui.GetClassName(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                rect = win32gui.GetWindowRect(hwnd)

                window_info = WindowInfo(
                    window_id=hwnd,
                    title=title,
                    class_name=class_name or "",
                    pid=pid,
                    is_visible=bool(win32gui.IsWindowVisible(hwnd)),
                    rect=Rect.from_tuple(rect),
                )

                windows.append(window_info)

            except Exception:
                pass

            return True

        win32gui.EnumWindows(enum_callback, None)
        return windows

    def focus_window(self, window_id: int) -> bool:
        try:
            if win32gui.IsIconic(window_id):
                win32gui.ShowWindow(window_id, win32con.SW_RESTORE)

            win32gui.SetForegroundWindow(window_id)
            win32gui.ShowWindow(window_id, win32con.SW_SHOW)

            return True
        except Exception:
            return False

    def get_window_rect(self, window_id: int) -> Optional[Rect]:
        try:
            rect_tuple = win32gui.GetWindowRect(window_id)
            return Rect.from_tuple(rect_tuple)
        except Exception:
            return None

    def get_client_rect(self, window_id: int) -> Optional[Rect]:
        try:
            client = win32gui.GetClientRect(window_id)
            left, top = win32gui.ClientToScreen(window_id, (client[0], client[1]))
            right, bottom = win32gui.ClientToScreen(window_id, (client[2], client[3]))
            return Rect(left=left, top=top, right=right, bottom=bottom)
        except Exception:
            return None
