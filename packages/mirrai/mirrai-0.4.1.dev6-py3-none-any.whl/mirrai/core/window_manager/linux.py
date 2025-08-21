import os
from typing import TYPE_CHECKING, List, Optional, Tuple

from mirrai.core.constants import IS_LINUX

if TYPE_CHECKING:
    from Xlib.display import Window  # type: ignore

if IS_LINUX:
    from ewmh import EWMH  # type: ignore
    from Xlib import X, display  # type: ignore
    from Xlib.error import BadWindow  # type: ignore

from mirrai.core.logger import logger
from mirrai.core.window_manager.base import WindowManager
from mirrai.core.window_manager.models import Rect, WindowInfo


class LinuxWindowManager(WindowManager):
    """Linux implementation of WindowManager using X11/EWMH."""

    def __init__(self):
        self._check_display_server()
        self._ewmh = EWMH()
        self._display = display.Display()
        self._root = self._display.screen().root

    def _check_display_server(self) -> None:
        """Check if running on X11 or Wayland and raise error if Wayland."""
        if "WAYLAND_DISPLAY" in os.environ:
            logger.error("Wayland detected but not supported")
            raise NotImplementedError("Wayland is not yet supported.")

        if "DISPLAY" not in os.environ:
            logger.error("No DISPLAY environment variable found")
            raise RuntimeError("X11 display not found.")

        logger.debug(f"Using X11 display: {os.environ.get('DISPLAY')}")

    def get_focused_window(self) -> Optional[int]:
        try:
            active_window = self._ewmh.getActiveWindow()
            if active_window:
                return active_window.id
            return None
        except Exception:
            return None

    def find_window_by_id(self, window_id: int) -> Optional[WindowInfo]:
        try:
            window = self._display.create_resource_object("window", window_id)
            wm_name = self._get_window_name(window)
            wm_class = self._get_window_class(window)
            pid = self._get_window_pid(window)
            geometry = self._get_window_geometry(window)

            if not geometry:
                return None

            return WindowInfo(
                window_id=window_id,
                title=wm_name or "",
                class_name=wm_class or "",
                pid=pid or 0,
                is_visible=self._is_window_visible(window),
                rect=Rect(
                    left=geometry[0],
                    top=geometry[1],
                    right=geometry[0] + geometry[2],
                    bottom=geometry[1] + geometry[3],
                ),
            )
        except Exception as e:
            logger.debug(f"Error finding window by ID {window_id}: {e}")
            return None

    def list_windows(self, filter_visible: bool = True) -> List[WindowInfo]:
        windows = []

        try:
            client_list = self._ewmh.getClientList()

            if not client_list:
                return windows

            for window in client_list:
                if not window:
                    continue
                try:
                    wm_name = self._get_window_name(window)

                    if filter_visible and not wm_name:
                        continue

                    is_visible = self._is_window_visible(window)
                    if filter_visible and not is_visible:
                        continue

                    wm_class = self._get_window_class(window)
                    pid = self._get_window_pid(window)
                    geometry = self._get_window_geometry(window)

                    if geometry:
                        window_info = WindowInfo(
                            window_id=window.id,
                            title=wm_name or "",
                            class_name=wm_class or "",
                            pid=pid or 0,
                            is_visible=is_visible,
                            rect=Rect(
                                left=geometry[0],
                                top=geometry[1],
                                right=geometry[0] + geometry[2],
                                bottom=geometry[1] + geometry[3],
                            ),
                        )
                        windows.append(window_info)

                except (BadWindow, Exception) as e:
                    logger.debug(f"Error processing window: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Error listing windows: {e}")

        return windows

    def focus_window(self, window_id: int) -> bool:
        try:
            window = self._display.create_resource_object("window", window_id)

            self._ewmh.setActiveWindow(window)
            self._ewmh.display.flush()
            window.configure(stack_mode=X.Above)
            window.set_input_focus(X.RevertToParent, X.CurrentTime)
            self._display.sync()

            return True
        except Exception as e:
            logger.debug(f"Error focusing window {window_id}: {e}")
            return False

    def get_window_rect(self, window_id: int) -> Optional[Rect]:
        try:
            window = self._display.create_resource_object("window", window_id)
            geometry = self._get_window_geometry(window)

            if geometry:
                return Rect(
                    left=geometry[0],
                    top=geometry[1],
                    right=geometry[0] + geometry[2],
                    bottom=geometry[1] + geometry[3],
                )
            return None
        except Exception:
            return None

    def get_client_rect(self, window_id: int) -> Optional[Rect]:
        try:
            window = self._display.create_resource_object("window", window_id)

            # Use geometry helper that handles coordinate translation
            geometry = self._get_window_geometry(window)

            if geometry:
                return Rect(
                    left=geometry[0],
                    top=geometry[1],
                    right=geometry[0] + geometry[2],
                    bottom=geometry[1] + geometry[3],
                )
            return None
        except Exception:
            return None

    def _get_window_name(self, window: "Window") -> Optional[str]:
        """Get window name/title."""
        try:
            net_wm_name = self._ewmh.getWmName(window)
            if net_wm_name:
                return net_wm_name

            wm_name = window.get_wm_name()
            if wm_name:
                return wm_name

        except Exception:
            pass
        return None

    def _get_window_class(self, window: "Window") -> Optional[str]:
        """Get window class name."""
        try:
            wm_class = window.get_wm_class()
            if wm_class and len(wm_class) > 1:
                return wm_class[1]
            elif wm_class:
                return wm_class[0]
        except Exception:
            pass
        return None

    def _get_window_pid(self, window: "Window") -> Optional[int]:
        """Get window process ID."""
        try:
            net_wm_pid = self._ewmh.getWmPid(window)
            if net_wm_pid:
                return net_wm_pid
        except Exception:
            pass
        return None

    def _get_window_geometry(self, window: "Window") -> Optional[Tuple[int, int, int, int]]:
        """Get window geometry as (x, y, width, height)."""
        try:
            geometry = window.get_geometry()
            coords = window.translate_coords(self._root, 0, 0)

            if coords and geometry:
                x, y = coords.x, coords.y

                # Handle negative coordinates from virtual display offsets
                if x < 0:
                    x = abs(x)
                if y < -100:
                    y = abs(y)

                return (x, y, geometry.width, geometry.height)
        except Exception:
            pass
        return None

    def _is_window_visible(self, window: "Window") -> bool:
        """Check if window is visible."""
        try:
            wm_state = window.get_wm_state()
            if wm_state and wm_state.get("state") == 0:  # WithdrawnState
                return False

            net_wm_state = self._ewmh.getWmState(window)
            if net_wm_state:
                hidden_states = ["_NET_WM_STATE_HIDDEN", "_NET_WM_STATE_MINIMIZED"]
                for state in hidden_states:
                    if state in str(net_wm_state):
                        return False

            attributes = window.get_attributes()
            if attributes:
                return attributes.map_state != X.IsUnmapped

        except Exception:
            pass

        return True

    def __del__(self):
        """Cleanup X11 resources."""
        try:
            if hasattr(self, "_display"):
                self._display.close()
        except Exception:
            pass
