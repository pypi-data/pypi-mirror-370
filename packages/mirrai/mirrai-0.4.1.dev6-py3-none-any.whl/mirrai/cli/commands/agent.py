import asyncio
import os
import signal
import sys
from typing import Any, Dict, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from mirrai.core.constants import DEFAULT_PROVIDER
from mirrai.core.execution import ExecutionManager, ExecutionRequest
from mirrai.core.execution.events import StatusChangeEvent
from mirrai.core.execution.models import ExecutionStatus
from mirrai.core.terminal.constants import (
    CLI_BORDER_STYLE,
    CLI_HEADER_STYLE,
    CLI_TABLE_BOX_STYLE,
    CLI_WIDTH,
)
from mirrai.core.terminal.output import AgentOutput

UNIX_SIGNAL_EXIT_BASE = 128

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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
    """AI agent for desktop automation"""
    if ctx.invoked_subcommand is None:
        title = Text()
        title.append("🤖 ", style="bold")
        title.append("AI Agent", style=CLI_HEADER_STYLE)

        panel = Panel(
            "Run AI-powered desktop automation tasks",
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

        commands_table.add_row("run", "Execute an automation task")

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
            examples_text.append('mirrai agent run "click on the save button"\n', style="dim")
            examples_text.append('mirrai agent run "open notepad" --window Notepad\n', style="dim")
            examples_text.append('mirrai agent run "fill out the form" --quiet', style="dim")

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

            console.print("\n[dim]Tip: You can use 'mirrai run' as a shortcut![/dim]")

        console.print()

        raise typer.Exit()


async def wait_for_completion(execution):
    """Wait for execution to reach a terminal state."""
    completion_event = asyncio.Event()
    final_status = None

    async def on_status_change(event: StatusChangeEvent):
        nonlocal final_status
        if event.new_status in {
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        }:
            final_status = event.new_status
            completion_event.set()

    execution.events.status_changes.on_async(on_status_change)
    await completion_event.wait()
    return final_status


async def execute_task(
    task: str,
    window: Optional[str] = None,
    quiet: bool = False,
    model: Optional[str] = None,
    provider: str = DEFAULT_PROVIDER,
    provider_config: Optional[Dict[str, Any]] = None,
):
    manager = ExecutionManager()

    request = ExecutionRequest(
        task=task,
        window=window,
        quiet=quiet,
        model=model,
        provider=provider,
        provider_config=provider_config,
    )

    execution = await manager.create_execution(request)
    execution_id = execution.id

    output = AgentOutput(console=console, quiet=quiet)
    output.show_execution_info(
        execution_id=execution_id,
        task=task,
        provider=provider,
        model=model,
        window=window,
    )

    final_status = await wait_for_completion(execution)

    # Refresh execution state
    execution = await manager.get_execution(execution_id)

    if not quiet and final_status:
        error_msg = None
        if final_status == ExecutionStatus.FAILED:
            error_msg = f"Task failed: {execution.error or 'Unknown error'}"
        output.show_task_status(final_status, message=error_msg)

    return execution


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
) -> None:
    """Run an agent task with the specified parameters."""
    load_dotenv()

    if not provider:
        provider = os.getenv("MIRRAI_PROVIDER", DEFAULT_PROVIDER)

    if not api_key:
        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                console.print("[red]Error: ANTHROPIC_API_KEY not found[/red]")
                console.print("Set it via environment variable or --api-key option")
                raise typer.Exit(code=1)
        elif provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                console.print("[red]Error: OPENROUTER_API_KEY not found[/red]")
                console.print("Set it via environment variable or --api-key option")
                raise typer.Exit(code=1)
        else:
            console.print(f"[red]Error: Unknown provider '{provider}'[/red]")
            console.print("Supported providers: anthropic, openrouter")
            raise typer.Exit(code=1)

    provider_config = {"api_key": api_key}
    if base_url:
        provider_config["base_url"] = base_url

    if debug:
        os.environ["MIRRAI_DEBUG_MODE"] = "1"

    try:
        asyncio.run(
            execute_task(
                task=task,
                window=window,
                quiet=quiet,
                model=model,
                provider=provider,
                provider_config=provider_config,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        # Use platform-appropriate exit code for keyboard interrupt
        # windows: 1 (generic failure)
        # *nix: 128 + SIGINT (130)
        exit_code = 1 if sys.platform == "win32" else (UNIX_SIGNAL_EXIT_BASE + signal.SIGINT)
        raise typer.Exit(code=exit_code)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
