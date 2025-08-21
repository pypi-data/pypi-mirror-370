import subprocess


def run_ruff_format(file_path, console):
    """
    Run ruff format on the given file.
    """
    try:
        result = subprocess.run(
            ["ruff", "format", file_path], capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print(f"[bold green]Formatted:[/bold green] {file_path}")
        else:
            console.print(
                f"[bold red]Ruff format failed for {file_path}:[/bold red]\n{result.stderr}"
            )
    except Exception as e:
        console.print(f"[bold red]Error running ruff format: {e}[/bold red]")


def run_ruff_check(file_path, console, autofix=False):
    """
    Run ruff check on the given file.
    Run with --fix if autofix is enabled.
    """
    cmd = ["ruff", "check", file_path]
    if autofix:
        cmd.insert(2, "--fix")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[bold green]Ruff check passed:[/bold green] {file_path}")
        else:
            console.print(
                f"[bold red]Ruff check issues for {file_path}:[/bold red]\n{result.stdout}"
            )
    except Exception as e:
        console.print(f"[bold red]Error running ruff check: {e}[/bold red]")


def run_ty_check(file_path, console):
    """
    Run ty check on the given file.
    """
    try:
        result = subprocess.run(
            ["ty", "check", file_path], capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print(f"[bold green]Ty check passed:[/bold green] {file_path}")
        else:
            console.print(
                f"[bold red]Ty check issues for {file_path}:[/bold red]\n{result.stdout}"
            )
    except Exception as e:
        console.print(f"[red]Error running ty check: {e}[/red]")
