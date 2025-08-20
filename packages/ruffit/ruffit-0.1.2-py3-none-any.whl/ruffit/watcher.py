from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from .utils import run_ruff_format, run_ruff_check, run_ty_check
import time
import os


class PyFileMonitor(FileSystemEventHandler):
    def __init__(self, path=".", autofix=False):
        self.console = Console()
        self.path = path
        self.autofix = autofix
        self.observer = Observer()
        self.ruffit_dir = os.path.abspath(os.path.dirname(__file__))
        self._event_times = {}
        self._debounce_seconds = 0.5

    def _is_own_library(self, src_path):
        """
        Check if the given path is part of the ruffit library.
        """
        abs_path = os.path.abspath(src_path)
        return abs_path.startswith(self.ruffit_dir)

    def _debounced(self, src_path):
        """
        Check if the given path is currently being processed.
        """
        now = time.time()
        last_time = self._event_times.get(src_path, 0)
        if now - last_time < self._debounce_seconds:
            return True
        self._event_times[src_path] = now
        return False

    def on_modified(self, event):
        """
        Handle file modification events.
        """
        if event.is_directory:
            return
        if str(event.src_path).endswith(".py") and not self._is_own_library(
            event.src_path
        ):
            if not self._debounced(event.src_path):
                self.console.print(
                    f"[bold yellow]Modified:[/bold yellow] {event.src_path}"
                )
                run_ruff_format(event.src_path, self.console)
                run_ruff_check(event.src_path, self.console, autofix=self.autofix)
                run_ty_check(event.src_path, self.console)

    def on_created(self, event):
        """
        Handle file creation events.
        """
        if event.is_directory:
            return
        if str(event.src_path).endswith(".py") and not self._is_own_library(
            event.src_path
        ):
            if not self._debounced(event.src_path):
                self.console.print(f"[bold cyan]Created:[/bold cyan] {event.src_path}")

    def start(self):
        """
        Start the file monitor.
        """
        self.console.print(
            f"[bold green]ruffit has started; monitoring {os.path.abspath(self.path)} for .py file changes![/bold green]"
        )
        if self.autofix:
            self.console.print(
                "[bold blue]autofix is enabled; ruff check will run with --fix[/bold blue]"
            )
        self.observer.schedule(self, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.console.print("[bold red]exiting ruffit.[/bold red]")
            self.observer.stop()
        self.observer.join()
