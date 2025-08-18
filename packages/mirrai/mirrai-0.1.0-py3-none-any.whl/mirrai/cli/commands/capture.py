import time
from pathlib import Path
from typing import Optional

import typer
from PIL import Image
from rich.console import Console

from mirrai.core.screen_capture.factory import ScreenCaptureFactory
from mirrai.core.window_manager.factory import WindowManagerFactory
from mirrai.core.window_manager.models import Rect

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
console = Console()


@app.command()
def screen(
    output: Path = typer.Argument("screenshot.png", help="Output file path"),
    region: Optional[str] = typer.Option(None, help="Region as 'left,top,right,bottom'"),
):
    if region:
        try:
            coords = [int(x) for x in region.split(",")]
            if len(coords) != 4:
                raise ValueError
            region_rect = Rect(left=coords[0], top=coords[1], right=coords[2], bottom=coords[3])
        except (ValueError, AttributeError):
            console.print("[red]Invalid region format. Use: left,top,right,bottom[/red]")
            return
    else:
        region_rect = None

    screen_capture = ScreenCaptureFactory.get()
    console.print(f"Capturing screen...")
    image_array = screen_capture.capture_screen(region_rect)
    image = Image.fromarray(image_array)
    image.save(str(output))
    console.print(f"[green]OK[/green] Saved to {output}")


@app.command()
def window(
    window_spec: str = typer.Argument(
        ...,
        help="Window specification (e.g., 'Notepad', 'title:Notepad', 'id:12345', 'process:notepad', 'pid:1234')",
    ),
    output: Optional[Path] = typer.Argument(None, help="Output file path"),
    full: bool = typer.Option(False, "--full", "-f", help="Capture full window including borders"),
    focus_first: bool = typer.Option(
        True, "--focus/--no-focus", help="Focus window before capture"
    ),
):
    window_manager = WindowManagerFactory.get()
    screen_capture = ScreenCaptureFactory.get()

    win = window_manager.find_window(window_spec)
    if not win:
        console.print(f"[red]No window found matching '{window_spec}'[/red]")
        return

    if not output:
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in win.title[:30])
        output = Path(f"{safe_title}.png")

    if focus_first:
        window_manager.focus_window(win.window_id)
        time.sleep(0.5)

    console.print(f"Capturing window: {win.title}")
    image_array = screen_capture.capture_window(win.window_id, use_client_area=not full)

    if image_array is None:
        console.print("[red]Failed to capture window[/red]")
        return

    image = Image.fromarray(image_array)
    image.save(str(output))
    console.print(f"[green]OK[/green] Saved to {output}")
    console.print(f"  Size: {image_array.shape[1]}x{image_array.shape[0]}")
