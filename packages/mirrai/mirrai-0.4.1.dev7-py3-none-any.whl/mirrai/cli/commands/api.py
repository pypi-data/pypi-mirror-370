import os
from typing import Optional

import typer
import uvicorn
from dotenv import load_dotenv
from rich.box import DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mirrai.core.terminal.constants import (
    CLI_BORDER_STYLE,
    CLI_HEADER_STYLE,
    CLI_TABLE_BOX_STYLE,
    CLI_WIDTH,
)

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
    """Show available API commands when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        title = Text()
        title.append("🌐 ", style="bold")
        title.append("API Server", style=CLI_HEADER_STYLE)

        panel = Panel(
            "Control the Mirrai API server for remote access",
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

        commands_table.add_row("serve", "Start the API server")

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
            examples_text.append("mirrai api serve\n", style="dim")
            examples_text.append("mirrai api serve --port 8080\n", style="dim")
            examples_text.append("mirrai api serve --host 0.0.0.0 --reload", style="dim")

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
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8777, "--port", "-p", help="Port to bind to"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Anthropic API key"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
):
    """Start the Mirrai API server."""
    load_dotenv()

    # TODO: Implement provider support into API serve command
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    elif not os.getenv("ANTHROPIC_API_KEY"):
        error_text = Text()
        error_text.append("ANTHROPIC_API_KEY not found\n\n", style="bold red")
        error_text.append("Please set it via:\n", style="white")
        error_text.append("• Environment variable: ", style="dim")
        error_text.append("export ANTHROPIC_API_KEY=your-key\n", style="yellow")
        error_text.append("• Command line option: ", style="dim")
        error_text.append("--api-key your-key", style="yellow")

        error_panel = Panel(
            error_text,
            title="[bold red]⚠️  Configuration Error[/bold red]",
            border_style="red",
            box=CLI_TABLE_BOX_STYLE,
            padding=(1, 2),
            width=CLI_WIDTH,
        )

        console.print()
        console.print(error_panel)
        console.print()
        return

    url_host = "localhost" if host == "0.0.0.0" else host

    title = Text()
    title.append("🌐 ", style="bold")
    title.append("API Server", style=CLI_HEADER_STYLE)

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column("Key", style="bold cyan")
    info_table.add_column("Value", style="white")

    info_table.add_row("Host", host)
    info_table.add_row("Port", str(port))
    info_table.add_row("", "")
    info_table.add_row("📚 Docs", f"http://{url_host}:{port}/docs")
    info_table.add_row("📄 OpenAPI", f"http://{url_host}:{port}/openapi.json")

    if reload:
        info_table.add_row("", "")
        info_table.add_row("🔄 Auto-reload", "[yellow]Enabled[/yellow]")

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

    uvicorn.run(
        "mirrai.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
