from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from mirrai.core.window_manager.factory import WindowManagerFactory

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
console = Console()


@app.command("list")
def list_cmd(
    search: Optional[str] = typer.Argument(
        None, help="Search for window (e.g., 'Notepad', 'process:chrome', 'pid:1234')"
    ),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all windows including hidden"),
):
    window_manager = WindowManagerFactory.get()

    if search:
        window = window_manager.find_window(search)
        if window:
            console.print(f"\n[green]Found window:[/green]")
            console.print(f"  Title: {window.title}")
            console.print(f"  ID: {window.window_id}")
            console.print(f"  Class: {window.class_name}")
            console.print(f"  PID: {window.pid}")
            console.print(f"  Position: ({window.rect.left}, {window.rect.top})")
            console.print(f"  Size: {window.width}x{window.height}")
        else:
            console.print(f"[red]No window found matching '{search}'[/red]")
    else:
        windows = window_manager.list_windows(filter_visible=not show_all)

        if not windows:
            console.print("[yellow]No windows found[/yellow]")
            return

        table = Table(title="Windows", show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("ID", style="yellow")
        table.add_column("Class", style="green")
        table.add_column("Size", style="blue")

        for window in windows[:20]:
            table.add_row(
                window.title[:50],
                str(window.window_id),
                window.class_name,
                f"{window.width}x{window.height}",
            )

        console.print(table)
        if len(windows) > 20:
            console.print(f"\n[dim]Showing 20 of {len(windows)} windows[/dim]")


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
        console.print(f"[red]No window found matching '{window_spec}'[/red]")
        return

    if window_manager.focus_window(window.window_id):
        console.print(f"[green]OK[/green] Focused window: {window.title}")
    else:
        console.print(f"[red]Failed to focus window: {window.title}[/red]")


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
        console.print(f"[red]No window found matching '{window_spec}'[/red]")
        return

    client_rect = window_manager.get_client_rect(window.window_id)

    console.print(f"\n[bold cyan]Window Information[/bold cyan]")
    console.print(f"  Title: {window.title}")
    console.print(f"  ID: {window.window_id}")
    console.print(f"  Class: {window.class_name}")
    console.print(f"  Process ID: {window.pid}")
    console.print(f"  Visible: {window.is_visible}")
    console.print(f"\n[bold]Window Rectangle:[/bold]")
    console.print(f"  Position: ({window.rect.left}, {window.rect.top})")
    console.print(f"  Size: {window.width}x{window.height}")

    if client_rect:
        console.print(f"\n[bold]Client Rectangle:[/bold]")
        console.print(f"  Position: ({client_rect.left}, {client_rect.top})")
        console.print(f"  Size: {client_rect.width}x{client_rect.height}")
