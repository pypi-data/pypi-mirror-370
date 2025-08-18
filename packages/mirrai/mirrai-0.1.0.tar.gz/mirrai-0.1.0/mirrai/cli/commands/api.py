import os
from typing import Optional

import typer
import uvicorn
from dotenv import load_dotenv
from rich.console import Console

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
console = Console()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8777, "--port", "-p", help="Port to bind to"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Anthropic API key"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
):
    """Start the Mirrai API server."""
    load_dotenv()

    # Check for API key
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    elif not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: ANTHROPIC_API_KEY not found[/red]")
        console.print("Set it via environment variable or --api-key option")
        return

    console.print(f"[cyan]Starting Mirrai API server[/cyan]")
    console.print(f"[cyan]Host:[/cyan] {host}")
    console.print(f"[cyan]Port:[/cyan] {port}")
    console.print(f"[cyan]Docs:[/cyan] http://{host}:{port}/docs")
    console.print(f"[cyan]OpenAPI:[/cyan] http://{host}:{port}/openapi.json")

    # Run the server
    uvicorn.run(
        "mirrai.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
