import io
from pathlib import Path
from typing import Optional, Union

import mss
import numpy as np
from PIL import Image

from mirrai.core.constants import IS_MACOS
from mirrai.core.utils.macos_permissions import MacOSPermissions
from mirrai.core.window_manager.factory import WindowManagerFactory
from mirrai.core.window_manager.models import Rect


class ScreenCapture:
    """Cross-platform screen capture implementation using mss."""

    def __init__(self):
        self.window_manager = WindowManagerFactory.get()
        if IS_MACOS:
            MacOSPermissions.ensure_screen_recording()

    def capture_screen(self, region: Optional[Rect] = None) -> np.ndarray:
        """
        Capture the screen or a specific region.

        Args:
            region: Optional Rect to capture.
                   If None, captures the entire primary monitor.

        Returns:
            NumPy array of the captured image in RGB format (height, width, 3)
        """
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

            return img[:, :, [2, 1, 0]]  # BGRA -> RGB

    def capture_window(self, window_id: int, use_client_area: bool = True) -> Optional[np.ndarray]:
        """
        Capture a specific window.

        Args:
            window_id: Window identifier (HWND on Windows, X11 Window ID on Linux)
            use_client_area: If True, capture only the client area (excluding title bar).
                           If False, capture the entire window.

        Returns:
            NumPy array of the captured window in RGB format, or None if failed
        """
        from mirrai.core.logger import logger

        logger.debug(f"Capturing window {window_id}, use_client_area={use_client_area}")

        if use_client_area:
            rect = self.window_manager.get_client_rect(window_id)
        else:
            rect = self.window_manager.get_window_rect(window_id)

        if not rect:
            logger.error(f"Failed to get rect for window {window_id}")
            return None

        logger.debug(
            f"Window rect: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}"
        )

        return self.capture_screen(rect)

    def save_image(self, image: np.ndarray, path: Union[str, Path]) -> None:
        """
        Save an image to disk.

        Args:
            image: NumPy array in RGB format
            path: Path where to save the image
        """
        img = Image.fromarray(image)
        img.save(path)

    def image_to_bytes(self, image: np.ndarray, format: str = "PNG") -> bytes:
        """
        Convert an image to bytes.

        Args:
            image: NumPy array in RGB format
            format: Image format (PNG, JPEG, etc.)

        Returns:
            Image as bytes
        """
        img = Image.fromarray(image)
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return buffer.getvalue()

    def resize_image(
        self, image: np.ndarray, width: Optional[int] = None, height: Optional[int] = None
    ) -> np.ndarray:
        """
        Resize an image maintaining aspect ratio if only one dimension is specified.

        Args:
            image: NumPy array in RGB format
            width: Target width (if None, calculated from height)
            height: Target height (if None, calculated from width)

        Returns:
            Resized image as NumPy array in RGB format
        """
        h, w = image.shape[:2]

        if width and not height:
            height = int(h * width / w)
        elif height and not width:
            width = int(w * height / h)
        elif not width and not height:
            return image

        assert width is not None and height is not None

        img = Image.fromarray(image)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return np.array(img)
