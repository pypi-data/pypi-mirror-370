import os
from unittest.mock import patch
from ruffit.run import PyFileMonitor


class DummyEvent:
    def __init__(self, src_path, is_directory=False):
        self.src_path = src_path
        self.is_directory = is_directory


def test_ignores_own_library(tmp_path):
    monitor = PyFileMonitor()
    own_file = os.path.join(monitor.ruffit_dir, "foo.py")
    event = DummyEvent(own_file)
    with patch.object(monitor, "console") as mock_console:
        monitor.on_modified(event)  # type: ignore
        mock_console.print.assert_not_called()


def test_debounce(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "test.py"
    file_path.write_text("print('hi')")
    event = DummyEvent(str(file_path))
    with patch.object(monitor, "console") as mock_console:
        monitor.on_modified(event)  # type: ignore
        monitor.on_modified(event)  # type: ignore
        assert mock_console.print.call_count == 4


def test_format_and_check_called(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "test.py"
    file_path.write_text("print('hi')")
    event = DummyEvent(str(file_path))
    with (
        patch.object(monitor, "_format_with_ruff") as mock_format,
        patch.object(monitor, "_check_with_ruff") as mock_ruff,
        patch.object(monitor, "_check_with_ty") as mock_ty,
        patch.object(monitor, "console"),
    ):
        monitor.on_modified(event)  # type: ignore
        mock_format.assert_called_once_with(str(file_path))
        mock_ruff.assert_called_once_with(str(file_path))
        mock_ty.assert_called_once_with(str(file_path))


def test_on_created_prints(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "test.py"
    file_path.write_text("print('hi')")
    event = DummyEvent(str(file_path))
    with patch.object(monitor, "console") as mock_console:
        monitor.on_created(event)  # type: ignore
        mock_console.print.assert_called_once()


def test_ruff_check_error(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "bad.py"
    file_path.write_text("def f(:\n    pass")  # Syntax error
    with (
        patch.object(monitor, "console") as mock_console,
        patch("subprocess.run") as mock_run,
    ):
        # Simulate ruff check returning error
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "E999 SyntaxError: invalid syntax"
        monitor._check_with_ruff(str(file_path))
        # Check that any call contains the expected error substring
        found = any(
            "Ruff check issues for" in str(call.args[0])
            and "E999 SyntaxError: invalid syntax" in str(call.args[0])
            for call in mock_console.print.call_args_list
        )
        assert found, "Expected errsor message not found in console output"
