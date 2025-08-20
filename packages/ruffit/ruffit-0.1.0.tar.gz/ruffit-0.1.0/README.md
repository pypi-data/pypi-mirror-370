# ruffit

A Python CLI tool for monitoring `.py` files and automatically running code quality checks and formatting.

## Features
- Watches for changes to Python files in any folder you specify
- Debounces rapid file events to avoid duplicate triggers
- On modification, automatically runs:
  - `ruff format` to auto-format code
  - `ruff check` to lint and check for code issues
  - `ty check` to check type annotations
- Rich terminal output for clear, colorful feedback
- Flexible CLI: monitor any folder by name, or the whole project

## Installation

```sh
pip install ruffit
```
Or, for local development:
```sh
pip install -e .
```

## Usage

Monitor all Python files in the project:
```sh
ruffit all
```

Monitor only a specific folder (e.g., `tests`):
```sh
ruffit tests
```

If the folder does not exist, ruffit will print an error.

## Development & Testing

- Tests are in the `tests/` folder and use `pytest`.
- To install test dependencies:
  ```sh
  pip install .[test]
  ```
- To run tests:
  ```sh
  pytest
  ```

## Contributing
Pull requests and issues are welcome!

## License
MIT
