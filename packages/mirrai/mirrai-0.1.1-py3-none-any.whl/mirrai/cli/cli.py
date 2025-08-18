import typer
from rich.console import Console

from mirrai.cli.commands import agent, api, capture, window

app = typer.Typer(
    name="mirrai",
    help="AI-powered desktop automation with computer use tool integration",
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()

app.add_typer(window.app, name="window", help="Window management commands")
app.add_typer(capture.app, name="capture", help="Screen capture commands")
app.add_typer(agent.app, name="agent", help="AI agent for desktop automation")
app.add_typer(api.app, name="api", help="API server commands")


@app.command()
def version():
    from mirrai.core import __version__

    console.print(f"Mirrai Version: {__version__}")


if __name__ == "__main__":
    app()
