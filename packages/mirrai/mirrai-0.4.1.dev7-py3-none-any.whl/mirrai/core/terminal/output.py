import random
from typing import TYPE_CHECKING, Literal, Optional, Tuple

if TYPE_CHECKING:
    from mirrai.core.execution.models import ExecutionStatus
    from mirrai.core.window_manager.models import WindowInfo

from rich.align import Align
from rich.box import DOUBLE
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from mirrai.core.constants import PROVIDER_DEFAULT_MODELS
from mirrai.core.input_controller.base import MouseButton, ScrollDirection
from mirrai.core.terminal.constants import (
    CLI_PANEL_BOX_STYLE,
    CLI_WIDTH,
    LOADING_BOX_STYLE,
    MESSAGE_BOX_STYLE,
    SPINNER_STYLES,
    THINKING_WORDS,
    TOOL_BOX_STYLE,
)


class AgentOutput:
    """Formatted output for agent execution and tool actions."""

    def __init__(
        self, console: Optional[Console] = None, quiet: bool = False, width: int = CLI_WIDTH
    ):
        self.console = console or Console()
        self.quiet = quiet
        self.preferred_width = width
        self.live: Optional[Live] = None
        self.loading_text: str = ""
        self.loading_spinner: Optional[str] = None

    def _get_width(self) -> int:
        """Get the width to use, capped by terminal width."""
        terminal_width = self.console.width
        return (
            min(self.preferred_width, terminal_width - 2)
            if terminal_width
            else self.preferred_width
        )

    def show_message(self, role: Literal["assistant", "user"], content: str) -> None:
        """Display a message from the assistant or user."""
        if self.quiet:
            return

        if role == "assistant":
            display_content = Markdown(content)
            title = "[bold blue]>> ASSISTANT <<[/bold blue]"
            border_color = "blue"
        elif role == "user":
            display_content = Text(content, style="green")
            title = "[bold green]<< USER >>[/bold green]"
            border_color = "green"
        else:
            return

        panel = Panel(
            display_content,
            title=title,
            border_style=border_color,
            box=MESSAGE_BOX_STYLE,
            width=self._get_width(),
            padding=(1, 2),
        )
        self.console.print(panel)

    def show_screenshot(
        self, width: int, height: int, size_str: str, scaled_from: Optional[Tuple[int, int]] = None
    ) -> None:
        """Display screenshot capture info."""
        if self.quiet:
            return

        content = Table(show_header=False, box=None, padding=(0, 1))
        content.add_column("Property", style="cyan")
        content.add_column("Value", style="white")

        content.add_row("▢ Dimensions", f"{width} × {height}")
        if scaled_from:
            content.add_row("↻ Scaled from", f"{scaled_from[0]} × {scaled_from[1]}")
        content.add_row("▪ Size", size_str)

        panel = Panel(
            content,
            title="[bold green]\\[#] SCREENSHOT \\[#][/bold green]",
            border_style="green",
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
        )

        self.console.print(panel)

    def show_click(
        self,
        click_type: MouseButton,
        coordinate: list,
        actual_coord: Optional[Tuple[int, int]] = None,
        offset: Optional[Tuple[int, int]] = None,
    ) -> None:
        """Display click action."""
        if self.quiet:
            return

        coord_text = f"[{coordinate[0]}, {coordinate[1]}]"
        if offset and (offset[0] != 0 or offset[1] != 0):
            coord_text += f" + offset [{offset[0]}, {offset[1]}]"
        if actual_coord:
            coord_text += f" → [{actual_coord[0]}, {actual_coord[1]}]"

        content = Text()
        content.append("◎ ", style="bold")
        content.append(coord_text, style="cyan")

        color = "blue"
        border = "blue"

        panel = Panel(
            content,
            title=f"[bold {color}](•) {click_type.value.upper()} CLICK (•)[/bold {color}]",
            border_style=border,
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 2),
        )

        self.console.print(panel)

    def show_typing(self, text: str) -> None:
        """Display typing action."""
        if self.quiet:
            return

        display_text = text if len(text) <= 50 else f"{text[:47]}..."

        content = Text()
        content.append("» ", style="bold")
        content.append(f'"{display_text}"', style="green")
        color = "green"

        panel = Panel(
            content,
            title=f"[bold {color}]--- TYPING ---[/bold {color}]",
            border_style=color,
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 2),
        )

        self.console.print(panel)

    def show_key_press(self, key: str) -> None:
        """Display key press action."""
        if self.quiet:
            return

        special_keys = {
            "Return": "⏎ Enter",
            "Tab": "⇥ Tab",
            "Escape": "⎋ Esc",
            "BackSpace": "⌫ Backspace",
            "Delete": "⌦ Delete",
            "space": "⎵ Space",
            "Up": "↑ Up",
            "Down": "↓ Down",
            "Left": "← Left",
            "Right": "→ Right",
        }

        display_key = special_keys.get(key, f"[{key}]")

        content = Text()
        content.append("Key: ", style="dim")
        content.append(display_key, style="bold cyan")
        color = "cyan"

        panel = Panel(
            content,
            title=f"[bold {color}]\\[^] KEY PRESS \\[^][/bold {color}]",
            border_style=color,
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 2),
        )

        self.console.print(panel)

    def show_mouse_move(
        self,
        coordinate: list,
        actual_coord: Optional[Tuple[int, int]] = None,
        offset: Optional[Tuple[int, int]] = None,
    ) -> None:
        """Display mouse move action."""
        if self.quiet:
            return

        coord_text = f"[{coordinate[0]}, {coordinate[1]}]"
        if offset and (offset[0] != 0 or offset[1] != 0):
            coord_text += f" + offset [{offset[0]}, {offset[1]}]"
        if actual_coord:
            coord_text += f" → [{actual_coord[0]}, {actual_coord[1]}]"

        content = Text()
        content.append("✧ ", style="bold")
        content.append(coord_text, style="magenta")
        color = "magenta"

        panel = Panel(
            content,
            title=f"[bold {color}]-> MOUSE MOVE <-[/bold {color}]",
            border_style=color,
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 2),
        )

        self.console.print(panel)

    def show_scroll(self, direction: ScrollDirection, amount: int) -> None:
        """Display scroll action."""
        if self.quiet:
            return

        arrow_map = {
            ScrollDirection.UP: "↑",
            ScrollDirection.DOWN: "↓",
            ScrollDirection.LEFT: "←",
            ScrollDirection.RIGHT: "→",
        }
        arrow = arrow_map.get(direction, "↕")

        content = Text()
        content.append(f"{arrow} ", style="bold")
        content.append(f"Scrolling {direction.value} by {amount} units", style="blue")
        color = "blue"

        panel = Panel(
            content,
            title=f"[bold {color}]↕ SCROLL ↕[/bold {color}]",
            border_style=color,
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 2),
        )

        self.console.print(panel)

    def show_wait(self, duration: float) -> None:
        """Display wait action."""
        if self.quiet:
            return

        content = Text()
        content.append("⧗ ", style="bold")
        content.append(
            f"Waiting for {duration} second{'s' if duration != 1 else ''}", style="magenta"
        )

        panel = Panel(
            content,
            title="[bold magenta]... WAIT ...[/bold magenta]",
            border_style="magenta",
            box=TOOL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 2),
        )

        self.console.print(panel)

    def start_loading(
        self, text: Optional[str] = None, spinner_style: Optional[str] = None
    ) -> None:
        """Start the loading indicator at the bottom of the terminal.

        Args:
            text: The text to display. If None, uses a random thinking word.
            spinner_style: The spinner style. If None, uses a random style.
        """
        if self.quiet or self.live:
            return

        if text is None:
            text = random.choice(THINKING_WORDS)

        if spinner_style is None:
            spinner_style = random.choice(SPINNER_STYLES)

        self.loading_text = text + "..."
        self.loading_spinner = spinner_style

        spinner = Spinner(
            self.loading_spinner or "dots", text=Text(f" {self.loading_text}", style="cyan")
        )
        centered = Align.center(spinner)
        panel = Panel(
            centered,
            box=LOADING_BOX_STYLE,
            border_style="cyan",
            width=self._get_width(),
            padding=(0, 1),
        )

        self.live = Live(panel, console=self.console, refresh_per_second=10, transient=True)
        self.live.start()

    def update_loading(self, text: str) -> None:
        """Update the loading indicator text."""
        if self.quiet or not self.live:
            return

        self.loading_text = text
        spinner = Spinner(
            self.loading_spinner or "dots", text=Text(f" {self.loading_text}", style="cyan")
        )
        centered = Align.center(spinner)
        panel = Panel(
            centered,
            box=LOADING_BOX_STYLE,
            border_style="cyan",
            width=self._get_width(),
            padding=(0, 1),
        )
        self.live.update(panel)

    def stop_loading(self) -> None:
        """Stop the loading indicator."""
        if self.live:
            self.live.stop()
            self.live = None
            self.loading_text = ""
            self.loading_spinner = None

    def show_execution_info(
        self,
        execution_id: str,
        task: str,
        provider: str,
        model: Optional[str] = None,
        window: Optional[str] = None,
    ) -> None:
        """Display the agent execution info panel."""
        if self.quiet:
            return

        title = Text()
        title.append("[=] AGENT EXECUTION [=]", style="bold cyan")

        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Key", style="bold cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Execution ID", execution_id)
        info_table.add_row("Task", task)
        if window:
            info_table.add_row("Target Window", window)
        info_table.add_row("Provider", provider)

        if model:
            info_table.add_row("Model", model)
        else:
            default_model = PROVIDER_DEFAULT_MODELS.get(provider, "unknown")
            info_table.add_row("Model", f"{default_model} (provider default)")

        panel = Panel(
            info_table,
            title=str(title),
            border_style="cyan",
            box=DOUBLE,
            padding=(1, 2),
            width=self._get_width(),
        )

        self.console.print()
        self.console.print(panel)

    def show_focused_window(self, window: "WindowInfo") -> None:
        """Display the focused window info."""
        if self.quiet:
            return

        title = Text()
        title.append("[>] WINDOW FOCUS [<]", style="bold cyan")

        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Property", style="bold cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Title", window.title)
        info_table.add_row("Position", f"({window.rect.left}, {window.rect.top})")
        info_table.add_row("Size", f"{window.rect.width} × {window.rect.height}")

        focus_panel = Panel(
            info_table,
            title=str(title),
            border_style="cyan",
            box=CLI_PANEL_BOX_STYLE,
            width=self._get_width(),
            padding=(0, 1),
        )
        self.console.print(focus_panel)

    def show_task_status(self, status: "ExecutionStatus", message: Optional[str] = None) -> None:
        """Display task completion status."""
        if self.quiet:
            return

        from mirrai.core.execution.models import ExecutionStatus

        if status == ExecutionStatus.COMPLETED:
            title = None
            content = Align.center(Text("Agent Execution Completed", style="bold italic green"))
            border_color = "green"
        elif status == ExecutionStatus.FAILED:
            title = Text("[✗] TASK FAILED [✗]", style="bold red")
            content = Text(message or "Task failed", style="red")
            border_color = "red"
        elif status == ExecutionStatus.CANCELLED:
            title = Text("[!] TASK CANCELLED [!]", style="bold yellow")
            content = Text("Task cancelled by user", style="yellow")
            border_color = "yellow"
        else:
            return

        panel = Panel(
            content,
            title=str(title) if title else None,
            border_style=border_color,
            box=DOUBLE,
            width=self._get_width(),
            padding=(0, 1),
        )

        self.console.print(panel)
