import asyncio
import os
import signal
import sys
from typing import Any, Dict, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from mirrai.core.constants import DEFAULT_PROVIDER, PROVIDER_DEFAULT_MODELS
from mirrai.core.execution import ExecutionManager, ExecutionRequest
from mirrai.core.execution.events import (
    ErrorEvent,
    MessageEvent,
    StatusChangeEvent,
)
from mirrai.core.execution.models import ExecutionState, ExecutionStatus

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
    model: Optional[str] = None,
    provider: Optional[str] = None,
    provider_config: Optional[Dict[str, Any]] = None,
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
        model=model,
        provider=provider,
        provider_config=provider_config,
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
    verbose: bool = typer.Option(True, "--verbose/--quiet", "-v/-q", help="Verbose output"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Log actions without executing them"),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Debug mode (shows screenshots before sending)"
    ),
) -> None:
    """Run an agent task with the specified parameters."""
    load_dotenv()

    # Use MIRRAI_PROVIDER env var as fallback if provider not specified
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

    console.print(f"[cyan]Starting agent task:[/cyan] {task}")

    if window:
        console.print(f"[cyan]Target window:[/cyan] {window}")

    console.print(f"[cyan]Provider:[/cyan] {provider}")
    if model:
        console.print(f"[cyan]Model:[/cyan] {model}")
    else:
        default_model = PROVIDER_DEFAULT_MODELS.get(provider, "unknown")
        console.print(f"[cyan]Model:[/cyan] {default_model} (provider default)")

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
