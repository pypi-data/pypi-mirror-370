import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import numpy as np
from PIL import Image

from mirrai.core.window_manager.models import Rect


class ScreenCapture(ABC):
    """Abstract base class for screen capture across platforms."""

    @abstractmethod
    def capture_screen(self, region: Optional[Rect] = None) -> np.ndarray:
        """
        Capture the screen or a specific region.

        Args:
            region: Optional Rect to capture.
                   If None, captures the entire primary monitor.

        Returns:
            NumPy array of the captured image in RGB format (height, width, 3)
        """
        pass

    @abstractmethod
    def capture_window(self, window_id: int, use_client_area: bool = True) -> Optional[np.ndarray]:
        """
        Capture a specific window.

        Args:
            window_id: Window identifier (HWND on Windows)
            use_client_area: If True, capture only the client area (excluding title bar).
                           If False, capture the entire window.

        Returns:
            NumPy array of the captured window in RGB format, or None if failed
        """
        pass

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
