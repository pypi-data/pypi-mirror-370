import sys

from invoke.context import Context
from invoke.tasks import task
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

BLACK = "uv run black"
ISORT = "uv run isort"
BASEDPYRIGHT = "uv run basedpyright"

__all__ = [
    "install",
    "typecheck",
    "format",
    "lint",
    "clean",
    "build",
    "publish",
    "help",
    "fmt",
    "tc",
]


@task
def install(c: Context):
    """Install the project and all dependencies with uv."""
    console.print("[bold green]Installing dependencies...[/bold green]")
    c.run("uv sync --all-extras")
    console.print("[bold green]✓[/bold green] Installation complete!")


@task
def typecheck(c: Context):
    """Run type checking for both Python and TypeScript code."""
    console.print(Panel("[bold blue]Type Checking", expand=False))

    # Python type checking
    console.print("\n[cyan]Python:[/cyan]")
    result = c.run(f"{BASEDPYRIGHT}", warn=True)
    if result and result.ok:
        console.print("  [green]✓[/green] Python type check passed")
    else:
        console.print("  [red]✗[/red] Python type check failed")

    # TypeScript type checking
    console.print("\n[cyan]TypeScript:[/cyan]")
    with c.cd("ui"):
        result = c.run("npm run type-check", warn=True)
    if result and result.ok:
        console.print("  [green]✓[/green] TypeScript type check passed")
    else:
        console.print("  [red]✗[/red] TypeScript type check failed")


@task
def format(c: Context, check: bool = False):
    """Format code with black/isort (Python) and prettier (TypeScript)."""
    action = "Checking" if check else "Formatting"
    console.print(Panel(f"[bold blue]{action} Code", expand=False))

    # Python formatting
    console.print("\n[cyan]Python:[/cyan]")
    if check:
        black_result = c.run(f"{BLACK} . --check --diff", warn=True)
        isort_result = c.run(f"{ISORT} . --check-only --diff", warn=True)
        if black_result and black_result.ok and isort_result and isort_result.ok:
            console.print("  [green]✓[/green] Python formatting is correct")
        else:
            console.print("  [yellow]![/yellow] Python formatting needs adjustment")
    else:
        c.run(f"{BLACK} .")
        c.run(f"{ISORT} .")
        console.print("  [green]✓[/green] Python code formatted")

    # TypeScript formatting
    console.print("\n[cyan]TypeScript:[/cyan]")
    with c.cd("ui"):
        if check:
            result = c.run("npm run format:check", warn=True)
            if result and result.ok:
                console.print("  [green]✓[/green] TypeScript formatting is correct")
            else:
                console.print("  [yellow]![/yellow] TypeScript formatting needs adjustment")
        else:
            c.run("npm run format")
            console.print("  [green]✓[/green] TypeScript code formatted")


@task
def lint(c: Context):
    """Run all linters (typecheck + format check)."""
    console.print(Panel("[bold magenta]Running All Linters", expand=False))
    console.print()
    typecheck(c)
    console.print()
    format(c, check=True)


@task
def clean(c: Context):
    """Clean build artifacts and caches."""
    console.print("[yellow]Cleaning build artifacts...[/yellow]")
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "build/",
        "dist/",
        "*.egg-info",
        ".pytest_cache",
        ".coverage",
        "htmlcov/",
    ]
    for pattern in patterns:
        if sys.platform == "win32":
            c.run(
                f"powershell -Command \"Remove-Item -Path '{pattern}' -Recurse -Force -ErrorAction SilentlyContinue\"",
                hide=True,
                warn=True,
            )
        else:
            c.run(f"rm -rf {pattern}", warn=True)
    console.print("[green]✓[/green] Cleaned!")


@task
def build(c: Context, clean_first: bool = True):
    """Build the package for distribution."""
    console.print(Panel("[bold blue]Building Package", expand=False))

    if clean_first:
        console.print("\n[yellow]Cleaning old builds...[/yellow]")
        c.run("rm -rf dist/ build/ *.egg-info", warn=True)

    console.print("\n[cyan]Building distributions...[/cyan]")
    result = c.run("uv run python -m build", warn=True)

    if result and result.ok:
        console.print("  [green]✓[/green] Package built successfully")
        # Show what was built
        c.run("ls -la dist/", hide=False)
    else:
        console.print("  [red]✗[/red] Build failed")
        sys.exit(1)


@task(pre=[build])
def publish(c: Context, repository: str = "pypi", config_file: str = ".pypirc"):
    """Publish package to PyPI (builds first)."""
    console.print(Panel(f"[bold green]Publishing to {repository.upper()}", expand=False))

    # Check the distributions first
    console.print("\n[cyan]Checking distributions...[/cyan]")
    check_result = c.run("uv run twine check dist/*", warn=True)

    if not check_result or not check_result.ok:
        console.print("  [red]✗[/red] Distribution check failed")
        sys.exit(1)

    console.print("  [green]✓[/green] Distribution check passed")

    # Upload
    console.print(f"\n[cyan]Uploading to {repository}...[/cyan]")
    cmd = f"uv run twine upload --config-file {config_file} dist/*"
    if repository == "testpypi":
        cmd += " --repository testpypi"

    result = c.run(cmd, warn=True)

    if result and result.ok:
        console.print(f"  [green]✓[/green] Successfully published to {repository}!")
        if repository == "pypi":
            console.print("\n[bold]Install with:[/bold] pip install mirrai")
        else:
            console.print(
                "\n[bold]Test install with:[/bold] pip install -i https://test.pypi.org/simple/ mirrai"
            )
    else:
        console.print(f"  [red]✗[/red] Upload to {repository} failed")
        sys.exit(1)


@task(default=True)
def help(c: Context):
    """Show available tasks."""
    _ = c

    # Commands table
    table = Table(
        title="[bold cyan]Mirrai Task Runner[/bold cyan]\nAvailable Commands",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Command", style="yellow", no_wrap=True)
    table.add_column("Description")
    table.add_column("Options", style="dim")
    table.add_row("invoke install", "Install project dependencies", "")
    table.add_row("invoke format", "Format code (Python & TypeScript)", "--check")
    table.add_row("invoke typecheck", "Run type checker (Python & TypeScript)", "")
    table.add_row("invoke lint", "Run all linters", "")
    table.add_row("invoke clean", "Clean build artifacts", "")
    table.add_row("invoke build", "Build package for distribution", "--no-clean-first")
    table.add_row("invoke publish", "Publish package to PyPI", "--repository, --config-file")
    console.print(table)

    # Examples
    console.print("\n[bold green]Examples:[/bold green]")
    examples_table = Table(show_header=False, box=None, padding=(0, 2))
    examples_table.add_column("Example", style="cyan")
    examples_table.add_row("invoke format --check")
    examples_table.add_row("invoke lint")
    examples_table.add_row("invoke clean")
    console.print(examples_table)

    # Footer
    console.print("\n[dim]Run 'invoke --list' for all available tasks[/dim]")
    console.print("[dim]Run 'invoke <task> --help' for detailed task options[/dim]\n")


@task(format)
def fmt(c: Context, check: bool = False):
    """Alias for format."""
    _, _ = c, check
    pass


@task(typecheck)
def tc(c: Context):
    """Alias for typecheck."""
    _ = c
    pass
