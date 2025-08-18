from fastapi import APIRouter, HTTPException

from mirrai.api.models import (
    FocusWindowResponse,
    WindowDetailResponse,
    WindowsResponse,
)
from mirrai.core.window_manager.factory import WindowManagerFactory

router = APIRouter(prefix="/windows", tags=["windows"])


@router.get("", response_model=WindowsResponse)
async def list_windows() -> WindowsResponse:
    """List all available windows."""
    try:
        window_manager = WindowManagerFactory.get()
        windows = window_manager.list_windows()

        # TODO: Add get_foreground_window to base class when implemented
        # to mark focused windows in the response

        # Convert to API models
        # Windows are already Pydantic models, just use them directly
        return WindowsResponse(windows=windows)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{window_spec}", response_model=WindowDetailResponse)
async def get_window(window_spec: str) -> WindowDetailResponse:
    """Get specific window details.

    Window spec can be:
    - A window title (default)
    - title:Window Title
    - id:12345 (window ID/HWND)
    - process:notepad (process name)
    - pid:1234 (process ID)
    """
    try:
        window_manager = WindowManagerFactory.get()

        # Find the window using the spec
        window = window_manager.find_window(window_spec)

        if not window:
            raise HTTPException(status_code=404, detail=f"Window not found: {window_spec}")

        # Get client rect
        client_rect = None
        try:
            client_rect = window_manager.get_client_rect(window.window_id)
        except:
            pass

        # Check if focused
        # TODO: Add get_foreground_window to base class when implemented
        is_focused = False

        return WindowDetailResponse(
            window_info=window,
            client_rect=client_rect,
            is_focused=is_focused,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{window_spec}/focus", response_model=FocusWindowResponse)
async def focus_window(window_spec: str) -> FocusWindowResponse:
    """Focus a window.

    Window spec can be:
    - A window title (default)
    - title:Window Title
    - id:12345 (window ID/HWND)
    - process:notepad (process name)
    - pid:1234 (process ID)
    """
    try:
        window_manager = WindowManagerFactory.get()

        # Find the window using the spec
        window = window_manager.find_window(window_spec)

        if not window:
            raise HTTPException(status_code=404, detail=f"Window not found: {window_spec}")

        # Focus the window
        success = window_manager.focus_window(window.window_id)

        return FocusWindowResponse(
            success=success,
            window_id=window.window_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
