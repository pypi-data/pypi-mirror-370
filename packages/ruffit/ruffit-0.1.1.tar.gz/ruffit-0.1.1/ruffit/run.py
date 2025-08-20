from rich.console import Console
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import threading
import subprocess
import sys


class PyFileMonitor(FileSystemEventHandler):
    def __init__(self, path="."):
        self.console: Console = Console()
        self.path: str = path
        self.observer = Observer()
        self.ruffit_dir: str = os.path.abspath(os.path.dirname(__file__))
        self._event_times: dict[str, float] = {}
        self._debounce_lock: threading.Lock = threading.Lock()
        self._debounce_seconds: float = 0.5

    def _is_own_library(self, src_path):
        abs_path = os.path.abspath(src_path)
        return abs_path.startswith(self.ruffit_dir)

    def _debounced(self, src_path):
        now = time.time()
        with self._debounce_lock:
            last_time = self._event_times.get(src_path, 0)
            if now - last_time < self._debounce_seconds:
                return True
            self._event_times[src_path] = now
            return False

    def on_modified(self, event):
        if event.is_directory:
            return
        if str(event.src_path).endswith(".py") and not self._is_own_library(
            event.src_path
        ):
            if not self._debounced(event.src_path):
                self.console.print(
                    f"[bold yellow]Modified:[/bold yellow] {event.src_path}"
                )
                self._format_with_ruff(event.src_path)
                self._check_with_ruff(event.src_path)
                self._check_with_ty(event.src_path)

    def _format_with_ruff(self, file_path):
        try:
            result = subprocess.run(
                ["ruff", "format", file_path], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.console.print(f"[bold green]Formatted:[/bold green] {file_path}")
            else:
                self.console.print(
                    f"[bold red]Ruff format failed for {file_path}:[/bold red]\n{result.stderr}"
                )
        except Exception as e:
            self.console.print(f"[bold red]Error running ruff format: {e}[/bold red]")

    def _check_with_ruff(self, file_path):
        import subprocess

        try:
            result = subprocess.run(
                ["ruff", "check", file_path], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.console.print(
                    f"[bold green]Ruff check passed:[/bold green] {file_path}"
                )
            else:
                self.console.print(
                    f"[bold red]Ruff check issues for {file_path}:[/bold red]\n{result.stdout}"
                )
        except Exception as e:
            self.console.print(f"[bold red]Error running ruff check: {e}[/bold red]")

    def _check_with_ty(self, file_path):
        try:
            result = subprocess.run(
                ["ty", "check", file_path], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.console.print(
                    f"[bold green]Ty check passed:[/bold green] {file_path}"
                )
            else:
                self.console.print(
                    f"[bold red]Ty check issues for {file_path}:[/bold red]\n{result.stdout}"
                )
        except Exception as e:
            self.console.print(f"[red]Error running ty check: {e}[/red]")

    def on_created(self, event):
        if event.is_directory:
            return
        if str(event.src_path).endswith(".py") and not self._is_own_library(
            event.src_path
        ):
            if not self._debounced(event.src_path):
                self.console.print(f"[bold cyan]Created:[/bold cyan] {event.src_path}")

    def start(self):
        self.console.print(
            f"[bold green]ruffit has started; monitoring {os.path.abspath(self.path)} for .py file changes![/bold green]"
        )
        self.observer.schedule(self, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.console.print("[bold red]Exiting ruffit.[/bold red]")
            self.observer.stop()
        self.observer.join()


def main():
    path = "."
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        if folder == "all":
            path = "."
        elif os.path.isdir(folder):
            path = folder
        else:
            console = Console()
            console.print(
                f"Folder '{folder}' does not exist; cannot monitor it.",
                style="bold red",
            )
            sys.exit(1)
    monitor = PyFileMonitor(path=path)
    monitor.start()
