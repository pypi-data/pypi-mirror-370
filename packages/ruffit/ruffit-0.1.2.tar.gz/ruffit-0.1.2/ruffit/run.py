import typer
from rich.console import Console
import os
from .watcher import PyFileMonitor

app = typer.Typer()


@app.command()
def main(
    folder: str = typer.Argument(
        ".", help="Folder to monitor (default: current directory)"
    ),
    autofix: bool = typer.Option(
        False, "--autofix", help="Enable autofix with ruff check"
    ),
):
    """
    Start the file monitor.
    """
    print(f"folder type: {type(folder)} value: {folder}")
    if folder != "." and folder != "all" and not os.path.isdir(folder):
        Console().print(
            f"Folder '{folder}' does not exist; cannot monitor it.", style="bold red"
        )
        raise typer.Exit(1)
    path = "." if folder == "all" else folder
    monitor = PyFileMonitor(path=path, autofix=autofix)
    monitor.start()


if __name__ == "__main__":
    app()
