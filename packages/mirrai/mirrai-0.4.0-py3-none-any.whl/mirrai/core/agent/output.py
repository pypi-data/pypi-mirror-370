from typing import Literal, Optional, Tuple

from rich.box import ROUNDED
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mirrai.core.input_controller.base import MouseButton, ScrollDirection


class AgentOutput:
    """Formatted output for agent execution and tool actions."""

    def __init__(self, console: Optional[Console] = None, quiet: bool = False):
        self.console = console or Console()
        self.quiet = quiet

    def show_message(self, role: Literal["assistant", "user"], content: str) -> None:
        """Display a message from the assistant or user."""
        if self.quiet:
            return

        if role == "assistant":
            md = Markdown(content)
            panel = Panel(
                md,
                title="🤖 [bold blue]Assistant[/bold blue]",
                border_style="blue",
                box=ROUNDED,
                expand=False,
                padding=(1, 2),
            )
            self.console.print(panel)
        elif role == "user":
            panel = Panel(
                Text(content, style="green"),
                title="👤 [bold green]User[/bold green]",
                border_style="green",
                box=ROUNDED,
                expand=False,
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

        content.add_row("📐 Dimensions", f"{width} × {height}")
        if scaled_from:
            content.add_row("🔄 Scaled from", f"{scaled_from[0]} × {scaled_from[1]}")
        content.add_row("💾 Size", size_str)

        panel = Panel(
            content,
            title="📸 [bold green]Screenshot Captured[/bold green]",
            border_style="green",
            box=ROUNDED,
            expand=False,
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

        click_emojis = {
            MouseButton.LEFT: "🖱️",
            MouseButton.RIGHT: "⚙️",
            MouseButton.DOUBLE: "⚡",
            MouseButton.MIDDLE: "🔘",
        }

        emoji = click_emojis.get(click_type, "🖱️")

        coord_text = f"[{coordinate[0]}, {coordinate[1]}]"
        if offset and (offset[0] != 0 or offset[1] != 0):
            coord_text += f" + offset [{offset[0]}, {offset[1]}]"
        if actual_coord:
            coord_text += f" → [{actual_coord[0]}, {actual_coord[1]}]"

        content = Text()
        content.append("📍 ", style="bold")
        content.append(coord_text, style="cyan")

        color = "blue"
        border = "blue"

        title = f"{emoji} {click_type.value.title()} Click"

        panel = Panel(
            content,
            title=f"[bold {color}]{title}[/bold {color}]",
            border_style=border,
            box=ROUNDED,
            expand=False,
            padding=(0, 1),
        )

        self.console.print(panel)

    def show_typing(self, text: str) -> None:
        """Display typing action."""
        if self.quiet:
            return

        display_text = text if len(text) <= 50 else f"{text[:47]}..."

        content = Text()
        content.append("⌨️  ", style="bold")
        content.append(f'"{display_text}"', style="green")
        color = "green"
        title = "Typing Text"

        panel = Panel(
            content,
            title=f"[bold {color}]💬 {title}[/bold {color}]",
            border_style=color,
            box=ROUNDED,
            expand=False,
            padding=(0, 1),
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
        title = "Key Press"

        panel = Panel(
            content,
            title=f"[bold {color}]⌨️ {title}[/bold {color}]",
            border_style=color,
            box=ROUNDED,
            expand=False,
            padding=(0, 1),
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
        content.append("🎯 ", style="bold")
        content.append(coord_text, style="magenta")
        color = "magenta"

        panel = Panel(
            content,
            title=f"[bold {color}]🐭 Mouse Move[/bold {color}]",
            border_style=color,
            box=ROUNDED,
            expand=False,
            padding=(0, 1),
        )

        self.console.print(panel)

    def show_scroll(self, direction: ScrollDirection, amount: int) -> None:
        """Display scroll action."""
        if self.quiet:
            return

        arrow_map = {
            ScrollDirection.UP: "⬆️",
            ScrollDirection.DOWN: "⬇️",
            ScrollDirection.LEFT: "⬅️",
            ScrollDirection.RIGHT: "➡️",
        }
        arrow = arrow_map.get(direction, "📜")

        content = Text()
        content.append(f"{arrow} ", style="bold")
        content.append(f"Scrolling {direction.value} by {amount} units", style="blue")
        color = "blue"

        panel = Panel(
            content,
            title=f"[bold {color}]📜 Scroll[/bold {color}]",
            border_style=color,
            box=ROUNDED,
            expand=False,
            padding=(0, 1),
        )

        self.console.print(panel)

    def show_wait(self, duration: float) -> None:
        """Display wait action."""
        if self.quiet:
            return

        content = Text()
        content.append("⏱️  ", style="bold")
        content.append(
            f"Waiting for {duration} second{'s' if duration != 1 else ''}", style="magenta"
        )

        panel = Panel(
            content,
            title="[bold magenta]⏸️ Wait[/bold magenta]",
            border_style="magenta",
            box=ROUNDED,
            expand=False,
            padding=(0, 1),
        )

        self.console.print(panel)
