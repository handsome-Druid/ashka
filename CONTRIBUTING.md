# Contributing

## Set Up the Development Environment

Initialize the development environment and install all development dependencies and optional features with:

```bash
uv sync --dev --all-extras
```

## Format and Lint

This project uses Ruff as both the formatter and linter. Run the following command before submitting changes:

```bash
uv run ruff check . --fix && uv run ruff format .
```

## Type Checking

This project uses Pyright for type checking. Run:

```bash
uv run pyright src tests
```

## Tests

Run the test suite with coverage before submitting changes:

```bash
uv run pytest --cov=ashka --cov-report=term-missing
```

## Before Opening a Pull Request

GitHub Actions runs the full test matrix for pull requests. You may first commit and push your changes to your own repository to verify CI before opening a pull request, or open the pull request directly and wait for the CI results in the main repository.
