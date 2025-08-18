"""Singleton logger for consistent output across core modules."""

from typing import Any

from rich.console import Console

from mirrai.core.utils import Singleton


class Logger(metaclass=Singleton):
    """Singleton logger for consistent output across core modules."""

    def __init__(self):
        """Initialize the logger with a Rich console."""
        self._console = Console()

    def debug(self, message: str) -> None:
        """Print debug message in yellow."""
        self._console.print(f"[yellow][DEBUG] {message}[/yellow]")

    def info(self, message: str) -> None:
        """Print info message in default color."""
        self._console.print(message)

    def warning(self, message: str) -> None:
        """Print warning message in yellow."""
        self._console.print(f"[yellow][WARNING] {message}[/yellow]")

    def error(self, message: str) -> None:
        """Print error message in red."""
        self._console.print(f"[red][ERROR] {message}[/red]")

    def success(self, message: str) -> None:
        """Print success message in green."""
        self._console.print(f"[green]{message}[/green]")

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Direct access to console.print."""
        self._console.print(*args, **kwargs)


logger = Logger()  # global singleton
