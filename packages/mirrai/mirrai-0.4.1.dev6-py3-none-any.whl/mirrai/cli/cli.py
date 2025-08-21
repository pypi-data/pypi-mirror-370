from typing import Optional

import typer
from rich.box import DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mirrai.cli.commands import agent, api, capture, window
from mirrai.core.terminal.constants import (
    CLI_BORDER_STYLE,
    CLI_HEADER_STYLE,
    CLI_PANEL_BOX_STYLE,
    CLI_WIDTH,
)

app = typer.Typer(
    name="mirrai",
    help="AI-powered desktop automation with computer use tool integration",
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=False,
    invoke_without_command=True,
)
console = Console()

app.add_typer(window.app, name="window", help="Window management commands")
app.add_typer(capture.app, name="capture", help="Screen capture commands")
app.add_typer(agent.app, name="agent", help="AI agent for desktop automation")
app.add_typer(api.app, name="api", help="API server commands")


@app.callback()
def main(
    ctx: typer.Context,
    examples: bool = typer.Option(False, "--examples", "-ex", help="Show usage examples"),
):
    """Show welcome screen when no command is provided."""
    if ctx.invoked_subcommand is None:
        from mirrai.core import __version__

        title = Text()
        title.append("mirrai", style=CLI_HEADER_STYLE)

        welcome_text = Text()
        welcome_text.append(f"Version {__version__}\n\n", style="dim")
        welcome_text.append(
            "AI-powered desktop automation with computer use capabilities.\n", style=""
        )
        welcome_text.append("Use natural language to control your desktop.\n", style="")

        panel = Panel(
            welcome_text,
            title=str(title),
            box=DOUBLE,
            border_style=CLI_BORDER_STYLE,
            padding=(1, 2),
            width=CLI_WIDTH,
        )
        console.print(panel)

        # Commands table
        commands_table = Table(
            title="[bold]Commands[/bold]",
            box=CLI_PANEL_BOX_STYLE,
            show_header=True,
            header_style=CLI_HEADER_STYLE,
            border_style=CLI_BORDER_STYLE,
            padding=(0, 1),
            width=CLI_WIDTH,
        )
        commands_table.add_column("Command", style=CLI_BORDER_STYLE, no_wrap=True)
        commands_table.add_column("Description", style="white")

        commands_table.add_row("run", "Run an automation task (alias for 'mirrai agent run')")
        commands_table.add_row("api", "API server commands")
        commands_table.add_row("capture", "Screen capture commands")
        commands_table.add_row("window", "Window management commands")
        commands_table.add_row("version", "Show version information")

        console.print(commands_table)

        # Options table
        options_table = Table(
            title="[bold]Options[/bold]",
            box=CLI_PANEL_BOX_STYLE,
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
        options_table.add_row("--install-completion", "Install shell completion")
        options_table.add_row("--show-completion", "Show completion script")

        console.print(options_table)

        if examples:
            # Examples in a panel
            examples_text = Text()
            examples_text.append('mirrai run "click on the save button"\n', style="dim")
            examples_text.append("mirrai window list\n", style="dim")
            examples_text.append("mirrai capture screen", style="dim")

            examples_panel = Panel(
                examples_text,
                title="[bold]Examples[/bold]",
                border_style="dim",
                box=CLI_PANEL_BOX_STYLE,
                padding=(0, 1),
                width=CLI_WIDTH,
            )

            console.print("\n")
            console.print(examples_panel)

        console.print()

        raise typer.Exit()


@app.command()
def run(
    task: str = typer.Argument(..., help="Task for agent to perform"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Target window title"),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (defaults to provider's default)"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="AI provider (anthropic, openrouter)"
    ),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key"),
    base_url: Optional[str] = typer.Option(
        None, "--base-url", help="Provider base URL (for OpenRouter)"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Hide the default task output"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Show additional debug logs"),
):
    """Run an automation task (alias for 'mirrai agent run')."""
    from mirrai.cli.commands.agent import run as agent_run

    agent_run(
        task=task,
        window=window,
        model=model,
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        quiet=quiet,
        debug=debug,
    )


@app.command()
def version():
    from mirrai.core import __version__

    console.print(f"Mirrai Version: {__version__}")


if __name__ == "__main__":
    app()
