from typing import Optional

import typer
from rich.box import DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mirrai.core.terminal.constants import (
    CLI_BORDER_STYLE,
    CLI_HEADER_STYLE,
    CLI_PANEL_BOX_STYLE,
    CLI_TABLE_BOX_STYLE,
    CLI_WIDTH,
)
from mirrai.core.window_manager.factory import WindowManagerFactory

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
    """Window management commands"""
    if ctx.invoked_subcommand is None:
        title = Text()
        title.append("🪟 ", style="bold")
        title.append("Window Management", style=CLI_HEADER_STYLE)

        panel = Panel(
            "Manage and interact with desktop windows",
            title=str(title),
            border_style=CLI_BORDER_STYLE,
            padding=(0, 2),
            width=CLI_WIDTH,
        )
        console.print(panel)

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

        commands_table.add_row("list", "List all windows or search")
        commands_table.add_row("focus", "Focus a window")
        commands_table.add_row("info", "Get detailed window info")

        console.print(commands_table)

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
            examples_text = Text()
            examples_text.append("mirrai window list\n", style="dim")
            examples_text.append("mirrai window list chrome\n", style="dim")
            examples_text.append('mirrai window focus "Visual Studio Code"', style="dim")

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


@app.command("list")
def list_cmd(
    search: Optional[str] = typer.Argument(
        None, help="Search for window (e.g., 'Notepad', 'process:chrome', 'pid:1234')"
    ),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all windows including hidden"),
):
    window_manager = WindowManagerFactory.get()

    if search:
        windows = window_manager.find_windows_by_title(title=search)
    else:
        windows = window_manager.list_windows(filter_visible=not show_all)

    if not windows:
        warning_text = Text()
        if search:
            warning_text.append(f"No windows found matching: ", style="white")
            warning_text.append(search, style="yellow")
        else:
            warning_text.append("No windows found", style="yellow")
            if not show_all:
                warning_text.append("\n\nTry using ", style="dim")
                warning_text.append("--all", style="yellow")
                warning_text.append(" to show hidden windows", style="dim")

        warning_panel = Panel(
            warning_text,
            title="[bold yellow]⚠️  No Windows[/bold yellow]",
            border_style="yellow",
            box=CLI_TABLE_BOX_STYLE,
            padding=(1, 2),
            width=CLI_WIDTH,
        )

        console.print()
        console.print(warning_panel)
        console.print()
        return

    title = Text()
    title.append("🪟 ", style="bold")
    if search:
        title.append(f"Windows matching '{search}'", style=CLI_HEADER_STYLE)
    elif show_all:
        title.append("All Windows", style=CLI_HEADER_STYLE)
    else:
        title.append("Visible Windows", style=CLI_HEADER_STYLE)

    table = Table(
        title=str(title),
        show_header=True,
        header_style=CLI_HEADER_STYLE,
        border_style=CLI_BORDER_STYLE,
        box=CLI_PANEL_BOX_STYLE,
        padding=(0, 1),
        width=CLI_WIDTH,
    )

    table.add_column("Title", style="white", no_wrap=False, width=35)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Class", style="yellow")
    table.add_column("Size", style="green", justify="right")

    for window in windows[:20]:
        title_display = window.title[:50] if window.title else "[dim]No title[/dim]"
        table.add_row(
            title_display,
            str(window.window_id),
            window.class_name or "[dim]Unknown[/dim]",
            f"{window.width} × {window.height}",
        )

    console.print()
    console.print(table)

    if len(windows) > 20:
        suffix = " matching your search." if search else ". Use search to find specific windows."
        console.print(f"\n[dim]Showing 20 of {len(windows)} windows{suffix}[/dim]")

    console.print()


@app.command()
def focus(
    window_spec: str = typer.Argument(
        ...,
        help="Window specification (e.g., 'Notepad', 'title:Notepad', 'id:12345', 'process:notepad', 'pid:1234')",
    )
):
    window_manager = WindowManagerFactory.get()
    window = window_manager.find_window(window_spec)
    if not window:
        error_text = Text()
        error_text.append(f"No window found matching: ", style="white")
        error_text.append(window_spec, style="yellow")

        error_panel = Panel(
            error_text,
            title="[bold red]⚠️  Window Not Found[/bold red]",
            border_style="red",
            box=CLI_TABLE_BOX_STYLE,
            padding=(1, 2),
            width=CLI_WIDTH,
        )

        console.print()
        console.print(error_panel)
        console.print()
        return

    if window_manager.focus_window(window.window_id):
        success_text = Text()
        success_text.append("✓ ", style="bold green")
        success_text.append("Successfully focused window:\n", style="green")
        success_text.append(window.title or "[No title]", style="white")

        success_panel = Panel(
            success_text,
            border_style="green",
            box=CLI_TABLE_BOX_STYLE,
            padding=(0, 2),
            width=CLI_WIDTH,
        )

        console.print()
        console.print(success_panel)
        console.print()
    else:
        error_text = Text()
        error_text.append("Failed to focus window:\n", style="red")
        error_text.append(window.title or "[No title]", style="white")

        error_panel = Panel(
            error_text,
            title="[bold red]⚠️  Focus Failed[/bold red]",
            border_style="red",
            box=CLI_TABLE_BOX_STYLE,
            padding=(1, 2),
            width=CLI_WIDTH,
        )

        console.print()
        console.print(error_panel)
        console.print()


@app.command()
def info(
    window_spec: str = typer.Argument(
        ...,
        help="Window specification (e.g., 'Notepad', 'title:Notepad', 'id:12345', 'process:notepad', 'pid:1234')",
    )
):
    window_manager = WindowManagerFactory.get()
    window = window_manager.find_window(window_spec)
    if not window:
        error_text = Text()
        error_text.append(f"No window found matching: ", style="white")
        error_text.append(window_spec, style="yellow")

        error_panel = Panel(
            error_text,
            title="[bold red]⚠️  Window Not Found[/bold red]",
            border_style="red",
            box=DOUBLE,
            padding=(1, 2),
            width=CLI_WIDTH,
        )

        console.print()
        console.print(error_panel)
        console.print()
        return

    title = Text()
    title.append("🪟 ", style="bold")
    title.append("Window Information", style=CLI_HEADER_STYLE)

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column("Property", style="bold cyan")
    info_table.add_column("Value", style="white")

    info_table.add_row("Title", window.title or "[dim]No title[/dim]")
    info_table.add_row("Window ID", str(window.window_id))
    info_table.add_row("Class", window.class_name or "[dim]Unknown[/dim]")
    info_table.add_row("Process ID", str(window.pid) if window.pid else "[dim]Unknown[/dim]")
    info_table.add_row("Visible", "[green]Yes[/green]" if window.is_visible else "[red]No[/red]")

    info_table.add_row("", "")
    info_table.add_row("[bold]Window Rectangle[/bold]", "")
    info_table.add_row("  Position", f"({window.rect.left}, {window.rect.top})")
    info_table.add_row("  Size", f"{window.width} × {window.height}")
    info_table.add_row("  Bottom-Right", f"({window.rect.right}, {window.rect.bottom})")

    client_rect = window_manager.get_client_rect(window.window_id)
    if client_rect:
        info_table.add_row("", "")
        info_table.add_row("[bold]Client Rectangle[/bold]", "")
        info_table.add_row("  Position", f"({client_rect.left}, {client_rect.top})")
        info_table.add_row("  Size", f"{client_rect.width} × {client_rect.height}")
        info_table.add_row("  Bottom-Right", f"({client_rect.right}, {client_rect.bottom})")

    panel = Panel(
        info_table,
        title=str(title),
        border_style=CLI_BORDER_STYLE,
        box=DOUBLE,
        padding=(1, 2),
        width=CLI_WIDTH,
    )

    console.print()
    console.print(panel)
    console.print()
