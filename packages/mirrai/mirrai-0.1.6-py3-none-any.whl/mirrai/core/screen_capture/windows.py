from typing import Optional

import mss
import numpy as np

from mirrai.core.screen_capture.base import ScreenCapture
from mirrai.core.window_manager.models import Rect
from mirrai.core.window_manager.windows import WindowsWindowManager


class WindowsScreenCapture(ScreenCapture):
    """Windows implementation of ScreenCapture using mss."""

    def __init__(self):
        self.window_manager = WindowsWindowManager()

    def capture_screen(self, region: Optional[Rect] = None) -> np.ndarray:
        with mss.mss() as sct:
            if region:
                monitor = {
                    "left": region.left,
                    "top": region.top,
                    "width": region.width,
                    "height": region.height,
                }
            else:
                monitor = sct.monitors[1]

            screenshot = sct.grab(monitor)
            img = np.array(screenshot)

            # mss returns BGRA, convert to RGB
            return img[:, :, [2, 1, 0]]  # BGRA -> RGB

    def capture_window(self, window_id: int, use_client_area: bool = True) -> Optional[np.ndarray]:
        if use_client_area:
            rect = self.window_manager.get_client_rect(window_id)
        else:
            rect = self.window_manager.get_window_rect(window_id)

        if not rect:
            return None

        return self.capture_screen(rect)
