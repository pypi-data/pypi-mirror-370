# Gemini Assistant Guide for fnb

This document provides a guide for developers interacting with the `fnb` project using Generative AIs.

You are a coding assistant for the `fnb` (Fetch'n'Backup) project.

Your main tasks are:
- Help implement CLI features using `Typer`
- Assist in managing and validating TOML-based configurations
- Support development of unit tests using `pytest`
- Maintain code quality using `ruff` and `pre-commit`
- Follow the coding style and constraints listed below


## About This Project

`fnb` (Fetch'n'Backup) is a simple, `rsync`-powered backup utility. It provides two core commands: `fetch` to pull data from a remote source, and `backup` to save that data to another location. The tool is configured via a simple TOML file.

- **Core Functionality**: `fetch`, `backup`, `sync` (fetch then backup).
- **Configuration**: Managed through `fnb.toml` files.
- **Technology**: A Python-based command-line interface (CLI) application.

## Tech Stack

- **Language**: Python 3.12+
- **Package Management**: `uv`
- **CLI Framework**: `Typer`
- **Configuration**: `Pydantic`
- **Testing**: `pytest`
- **Linting/Formatting**: `ruff`
- **Automation**: `pre-commit`, `Taskfile.yml`
- **Documentation**: `mkdocs`

## Project Structure

- `src/fnb/`: Main application source code.
  - `cli.py`: Entry point for the CLI application (Typer).
  - `config.py`: Configuration loading and validation (Pydantic).
  - `fetcher.py`, `backuper.py`: Core logic for `rsync` operations.
- `tests/`: Unit and integration tests.
- `docs/`: Documentation files for `mkdocs`
- `pyproject.toml`: Project metadata and dependencies.
- `Taskfile.yml`: Defines common development tasks.


## DO

- Always respond in **Japanese**, except for code and docstrings.
- Use **English** for all code, comments, and docstrings.
- Output **one function / class at a time**, with explanation.
- Follow **PEP8** naming conventions (`snake_case`)
- Use only predefined models/fuctions (e.g. `RsyncTaskConfig`, `ConfigReader`) unless approved.
- Insert `TODO` markers in docstrings when leaving suggestions for improvement.
- Follow **Conventional Commits** style in commit messages.
- Ask when unsure -- never assume functionality or structure.

## DO NOT

- Do not invent new functions, classes, arguments, or file structures.
- Do not use Japanese in code, comments, docstrings.
- Do not output multiple features or components in one response.
- Do not omit or remove `TODO` or existing discussion points.
- Do not write pseudocode unless explicitly asked.
- Do not change user-established naming, file organization, or conventions.

## Assumptions

- Configuration files are TOML (e.g., `fnb.toml`, `config.toml`)
- Each section is prefixed with `[fetch.xxx]` or `[backup.xxx]` structure
- Required config fields: `label`, `summary`, `host`, `source`, `target`, `options`, `enabled`.
- `.env` file may contain values such as `SSH_PASSWORD`,  and is automatically loaded via `python-dotenv`.
- SSH automation is handled using `pexpect`.

## Commit Rules

- Use **Conventional Commits** for all Git commit messages.
- Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Use scope (`cli`, `config`, `gear`, etc.) where helpful.
- For breaking changes, add `!` (e.g., `refactor!: change return type of run_rsync`)

## Development Workflow

All common development tasks are defined in `Taskfile.yml` and can be run with the `task` command.

Run common development tasks via `task`:

```bash
# Run tests with coverage
task pytest

# Serve documentation locally
task docs

# Format code
task format
```
