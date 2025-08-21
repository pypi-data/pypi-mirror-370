# For Developers

If you want to contribute to the development of this plugin, this guide will help you get started.

## Requirements

Before you begin, make sure you have the following tools installed:

- [**Python**](https://www.python.org/)
- [**uv**](https://github.com/astral-sh/uv)

## Setting up the Development Environment

To get started, clone the repository and install the project in editable mode with its development dependencies:

```bash
uv pip install -e '.[dev]'
```

This command should be used initially to set up your environment and whenever you add new dependencies to `pyproject.toml`.

## Running Tests

This project uses [**`pytest`**](https://docs.pytest.org/) for testing. To run the full test suite, execute the following command from the project's root directory:

```bash
uv run pytest
```

## Code Style

This project uses [**`Ruff`**](https://docs.astral.sh/ruff/) for linting and code formatting. To check your code for errors, run:

```bash
uv run ruff check .
```

To automatically format your code, run:

```bash
uv run ruff format .
```

## Submitting Changes

Before you submit a pull request, please make sure you have:

- Added your changes to the `CHANGELOG.md` file.
- Run the tests and ensured they all pass.
- Formatted your code with `ruff`.

## See Also

- [Why Use a Graph?](../explanation/why-use-a-graph.md)
- [Configuration](../reference/configuration.md)
- [Customization](../how-to/customization.md)
