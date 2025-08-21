import time
from pathlib import Path
from typing import Optional

import typer
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mirrai.core.capture import ScreenCapture
from mirrai.core.terminal.constants import (
    CLI_BORDER_STYLE,
    CLI_HEADER_STYLE,
    CLI_TABLE_BOX_STYLE,
    CLI_WIDTH,
)
from mirrai.core.window_manager.factory import WindowManagerFactory
from mirrai.core.window_manager.models import Rect

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=False,
)
console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    examples: bool = typer.Option(False, "--examples", "-ex", help="Show usage examples"),
):
    """Show available capture commands when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        title = Text()
        title.append("📸 ", style="bold")
        title.append("Screen Capture", style=CLI_HEADER_STYLE)

        panel = Panel(
            "Capture screenshots and screen information",
            title=str(title),
            border_style=CLI_BORDER_STYLE,
            padding=(0, 2),
            width=CLI_WIDTH,
        )
        console.print(panel)

        # Commands table
        commands_table = Table(
            title="[bold]Commands[/bold]",
            box=CLI_TABLE_BOX_STYLE,
            show_header=True,
            header_style=CLI_HEADER_STYLE,
            border_style=CLI_BORDER_STYLE,
            padding=(0, 1),
            width=CLI_WIDTH,
        )
        commands_table.add_column("Command", style=CLI_BORDER_STYLE, no_wrap=True)
        commands_table.add_column("Description", style="white")

        commands_table.add_row("screen", "Capture entire screen")
        commands_table.add_row("window", "Capture specific window")

        console.print(commands_table)

        # Options table
        options_table = Table(
            title="[bold]Options[/bold]",
            box=CLI_TABLE_BOX_STYLE,
            show_header=True,
            header_style=CLI_HEADER_STYLE,
            border_style=CLI_BORDER_STYLE,
            padding=(0, 1),
            width=CLI_WIDTH,
        )
        options_table.add_column("Option", style=CLI_BORDER_STYLE, no_wrap=True)
        options_table.add_column("Description", style="white")

        options_table.add_row("--help, -h", "Show help message")
        options_table.add_row("--examples, -ex", "Show usage examples")

        console.print(options_table)

        if examples:
            # Examples panel
            examples_text = Text()
            examples_text.append("mirrai capture screen\n", style="dim")
            examples_text.append("mirrai capture screen screenshot.png\n", style="dim")
            examples_text.append('mirrai capture window --search "Chrome"', style="dim")

            examples_panel = Panel(
                examples_text,
                title="[bold]Examples[/bold]",
                border_style="dim",
                box=CLI_TABLE_BOX_STYLE,
                padding=(0, 1),
                width=CLI_WIDTH,
            )

            console.print("\n")
            console.print(examples_panel)

        console.print()

        raise typer.Exit()


@app.command()
def screen(
    output: Path = typer.Argument("screenshot.png", help="Output file path"),
    region: Optional[str] = typer.Option(None, help="Region as 'left,top,right,bottom'"),
):
    if region:
        try:
            coords = [int(x) for x in region.split(",")]
            if len(coords) != 4:
                raise ValueError
            region_rect = Rect(left=coords[0], top=coords[1], right=coords[2], bottom=coords[3])
        except (ValueError, AttributeError):
            console.print("[red]Invalid region format. Use: left,top,right,bottom[/red]")
            return
    else:
        region_rect = None

    screen_capture = ScreenCapture()
    console.print(f"Capturing screen...")
    image_array = screen_capture.capture_screen(region_rect)
    image = Image.fromarray(image_array)
    image.save(str(output))
    console.print(f"[green]OK[/green] Saved to {output}")


@app.command()
def window(
    window_spec: str = typer.Argument(
        ...,
        help="Window specification (e.g., 'Notepad', 'title:Notepad', 'id:12345', 'process:notepad', 'pid:1234')",
    ),
    output: Optional[Path] = typer.Argument(None, help="Output file path"),
    full: bool = typer.Option(False, "--full", "-f", help="Capture full window including borders"),
    focus_first: bool = typer.Option(
        True, "--focus/--no-focus", help="Focus window before capture"
    ),
):
    window_manager = WindowManagerFactory.get()
    screen_capture = ScreenCapture()

    win = window_manager.find_window(window_spec)
    if not win:
        console.print(f"[red]No window found matching '{window_spec}'[/red]")
        return

    if not output:
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in win.title[:30])
        output = Path(f"{safe_title}.png")

    if focus_first:
        window_manager.focus_window(win.window_id)
        time.sleep(0.5)

    console.print(f"Capturing window: {win.title}")
    image_array = screen_capture.capture_window(win.window_id, use_client_area=not full)

    if image_array is None:
        console.print("[red]Failed to capture window[/red]")
        return

    image = Image.fromarray(image_array)
    image.save(str(output))
    console.print(f"[green]OK[/green] Saved to {output}")
    console.print(f"  Size: {image_array.shape[1]}x{image_array.shape[0]}")
