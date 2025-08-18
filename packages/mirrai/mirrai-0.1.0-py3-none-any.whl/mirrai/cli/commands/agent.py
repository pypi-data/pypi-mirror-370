import asyncio
import os
import signal
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from mirrai.core.client import client
from mirrai.core.execution import ExecutionManager, ExecutionRequest
from mirrai.core.execution.events import (
    ErrorEvent,
    MessageEvent,
    StatusChangeEvent,
)
from mirrai.core.execution.models import ExecutionState, ExecutionStatus

DEFAULT_MODEL = "claude-sonnet-4-20250514"
UNIX_SIGNAL_EXIT_BASE = 128

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
console = Console()


class ExecutionTracker:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.completion_event = asyncio.Event()
        self.final_status: Optional[ExecutionStatus] = None

    async def handle_message(self, event: MessageEvent) -> None:
        if not self.verbose:
            return

        role_color = "blue" if event.message.role == "assistant" else "green"
        console.print(
            f"[{role_color}]{event.message.role.capitalize()}:[/{role_color}] {event.message.content}"
        )

    async def handle_status_change(self, event: StatusChangeEvent) -> None:
        terminal_states = {
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        }

        if event.new_status in terminal_states:
            self.final_status = event.new_status
            self.completion_event.set()

    async def handle_error(self, event: ErrorEvent) -> None:
        if self.verbose:
            console.print(f"[red]Error: {event.error}[/red]")


async def execute_task(
    task: str,
    window: Optional[str] = None,
    execute_actions: bool = True,
    debug_mode: bool = False,
    verbose: bool = True,
) -> ExecutionState:
    manager = ExecutionManager()
    tracker = ExecutionTracker(verbose)

    manager.events.messages.on_async(tracker.handle_message)
    manager.events.status_changes.on_async(tracker.handle_status_change)
    manager.events.errors.on_async(tracker.handle_error)

    request = ExecutionRequest(
        task=task,
        window=window,
        execute_actions=execute_actions,
        debug_mode=debug_mode,
        # TODO: Add model selection to ExecutionRequest
    )

    execution = await manager.create_execution(request)
    execution_id = execution.id
    console.print(f"[cyan]Execution ID:[/cyan] {execution_id}")

    await tracker.completion_event.wait()

    execution = await manager.get_execution(execution_id)

    if tracker.final_status == ExecutionStatus.COMPLETED:
        console.print("\n[green]Task completed successfully![/green]")
    elif tracker.final_status == ExecutionStatus.FAILED:
        error_msg = execution.error or "Unknown error"
        console.print(f"\n[red]Task failed: {error_msg}[/red]")
    elif tracker.final_status == ExecutionStatus.CANCELLED:
        console.print("\n[yellow]Task cancelled[/yellow]")

    return execution


@app.command()
def run(
    task: str = typer.Argument(..., help="Task for agent to perform"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Target window title"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Anthropic model to use"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Anthropic API key"),
    verbose: bool = typer.Option(True, "--verbose/--quiet", "-v/-q", help="Verbose output"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Log actions without executing them"),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Debug mode (shows screenshots before sending)"
    ),
) -> None:
    """Run an agent task with the specified parameters.

    This is the main entry point for the CLI agent command.
    """
    load_dotenv()

    # Validate and set API key
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not found[/red]")
        console.print("Set it via environment variable or --api-key option")
        raise typer.Exit(code=1)

    client.set_api_key(api_key)

    console.print(f"[cyan]Starting agent task:[/cyan] {task}")

    if window:
        console.print(f"[cyan]Target window:[/cyan] {window}")

    console.print(f"[cyan]Model:[/cyan] {model}")

    mode = "Dry run (no actions executed)" if dry_run else "Live (actions will be executed)"
    console.print(f"[cyan]Mode:[/cyan] {mode}")

    if debug:
        console.print(
            "[cyan]Debug mode:[/cyan] Screenshots will be shown before sending to the agent"
        )

    console.print()

    try:
        asyncio.run(
            execute_task(
                task=task,
                window=window,
                execute_actions=not dry_run,
                debug_mode=debug,
                verbose=verbose,
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
