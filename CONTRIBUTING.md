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

## Before Opening a Pull Request

Before opening a pull request, first commit and push your changes to your own repository so that CI runs the full test matrix. Open the pull request only after the CI checks have completed successfully.
