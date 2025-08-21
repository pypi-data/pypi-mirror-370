import json
import subprocess
import time
from typing import Optional, Tuple

from mirrai.core.logger import logger
from mirrai.core.window_manager.linux import LinuxWindowManager


class I3WindowManager(LinuxWindowManager):
    """i3-specific window manager implementation."""

    def __init__(self):
        super().__init__()
        logger.debug("Using i3-specific window manager")

    def focus_window(self, window_id: int) -> bool:
        """Focus a window, switching workspaces if necessary."""
        try:
            # Get window info including container IDs
            info = self._get_window_info(window_id)
            if not info:
                logger.debug(f"Could not find window info for {window_id}")
                return super().focus_window(window_id)

            workspace, con_id, parent_id = info

            # Switch to the workspace first if needed
            if workspace:
                self._switch_to_workspace(workspace)

            # For windows in tabbed/stacked containers, we need to:
            # 1. Focus the parent container (activates the stack/tab group)
            # 2. Focus the child container (makes it visible)
            if parent_id and con_id:
                # Chain commands: focus parent container, then child container
                cmd = f'[con_id="{parent_id}"] focus; [con_id="{con_id}"] focus'
                logger.debug(f"Focusing parent {parent_id} then child {con_id}")
            else:
                # No parent container or not in a tabbed/stacked layout
                cmd = f'[con_id="{con_id}"] focus' if con_id else f'[id="{window_id}"] focus'
                logger.debug(
                    f"Direct focus on {'container' if con_id else 'window'} {con_id or window_id}"
                )

            result = subprocess.run(["i3-msg", cmd], capture_output=True, text=True, timeout=1)

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if isinstance(response, list) and all(
                        r.get("success", False) for r in response
                    ):
                        # Brief delay to allow i3 to render

                        time.sleep(0.05)
                        return True
                    else:
                        logger.debug(f"i3 focus command(s) failed: {response}")
                except Exception as e:
                    logger.debug(f"Error parsing i3 response: {e}")
                    # If we can't parse but return code was 0, assume success
                    return True

            logger.debug(f"i3 focus failed: {result.stderr}")
            # Fallback to standard EWMH method
            return super().focus_window(window_id)

        except Exception as e:
            logger.debug(f"Error in i3 focus_window: {e}")
            return super().focus_window(window_id)

    def _get_window_info(self, window_id: int) -> Optional[Tuple[str, int, Optional[int]]]:
        """Get workspace, container ID, and parent container ID for a window."""
        try:
            result = subprocess.run(
                ["i3-msg", "-t", "get_tree"], capture_output=True, text=True, timeout=1
            )
            if result.returncode != 0:
                return None

            tree = json.loads(result.stdout)

            def find_window(
                node: dict,
                target_id: int,
                workspace: Optional[str] = None,
                parent: Optional[dict] = None,
            ) -> Optional[Tuple[str, int, Optional[int]]]:
                # Track current workspace
                if node.get("type") == "workspace":
                    workspace = node.get("name")

                # Check if this node has our window
                if node.get("window") == target_id:
                    con_id = node.get("id")
                    parent_id = parent.get("id") if parent else None
                    # Ensure we have valid values before returning
                    if workspace and con_id:
                        return workspace, con_id, parent_id

                # Search children recursively
                for child in node.get("nodes", []) + node.get("floating_nodes", []):
                    result = find_window(child, target_id, workspace, node)
                    if result:
                        return result
                return None

            return find_window(tree, window_id)

        except Exception as e:
            logger.debug(f"Error getting window info: {e}")
            return None

    def _switch_to_workspace(self, workspace: str) -> bool:
        """Switch to the specified i3 workspace."""
        try:
            result = subprocess.run(
                ["i3-msg", f"workspace {workspace}"], capture_output=True, text=True, timeout=1
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Error switching to workspace {workspace}: {e}")
            return False
