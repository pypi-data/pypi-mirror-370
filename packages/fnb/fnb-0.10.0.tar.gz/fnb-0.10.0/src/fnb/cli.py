"""
cli.py

Command-line interface entry point for the fnb (Fetch'n'Backup) tool.

This script defines the main CLI commands using Typer:
- `fetch`: Pull data from remote server to local
- `backup`: Push local data to cloud or external backup
- `sync`: Run both fetch and backup sequentially
- `status`: Show the current status of all configured tasks
- `init`: Generate initial config files (.toml, .env)

Each command delegates to its corresponding module:
- fetch   -> fnb.fetcher
- backup  -> fnb.backuper
- status  -> fnb.reader
- init    -> fnb.generator

Shared options include:
- `--config`: Path to config file (default: auto-detect)
- `--dry-run`: Preview without making changes
- `--ssh-password`: For remote SSH login if required

Configuration is defined in a `config.toml` file, which can be initialized with:
    fnb init

To expose this CLI as a `fnb` command, set up `project.scripts` in pyproject.toml.
"""

from pathlib import Path

import typer

from fnb import __version__
from fnb import backuper, fetcher, generator
from fnb.reader import ConfigReader


app = typer.Typer(help="fnb - Fetch'n'Backup")


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"fnb version {__version__}")


@app.command()
def init(
    kind: str = typer.Argument(
        "all", help="Kind of configuration file to generate (all, config, env)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing file without confirmation"
    ),
) -> None:
    """Generate default configuration files in the current directory.

    Examples:
        fnb init        # Generate all config files
        fnb init config # Generate only fnb.toml
        fnb init env    # Generate only .env
    """
    try:
        # Convert str to ConfigKind
        generator.run(kind=kind.lower(), force=force)
    except ValueError as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def status(
    config: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: auto-detect)"
    ),
) -> None:
    """Show summary of enabled fetch/backup tasks defined in the config file."""
    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)
        reader.print_status()
    except FileNotFoundError:
        typer.echo("❌ No config file found. Run 'fnb init' to create one.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def fetch(
    label: str,
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        "-f",
        help="Force create target directory if it doesn't exist",
    ),
    ssh_password: str | None = typer.Option(
        None,
        "--ssh-password",
        "-p",
        help="Password for SSH authentication (overrides .env)",
    ),
    config: str = typer.Option(
        "./fnb.toml", "--config", "-c", help="Path to config file"
    ),
) -> None:
    """Fetch data from remote server based on the label specified in config.toml."""
    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)
        task = reader.config.get_task_by_label("fetch", label)

        if task is None:
            typer.echo(f"❌ Label not found: {label}")
            raise typer.Exit(1)

        fetcher.run(
            task,
            dry_run=dry_run,
            ssh_password=ssh_password,
            create_dirs=create_dirs,
        )

    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        typer.echo("Use --create-dirs option to create missing directories.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def backup(
    label: str,
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        "-f",
        help="Force create target directory if it doesn't exist",
    ),
    config: str = typer.Option(
        "./fnb.toml", "--config", "-c", help="Path to config file"
    ),
) -> None:
    """Backup data to external or another local target."""
    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)
        task = reader.config.get_task_by_label("backup", label)

        if task is None:
            typer.echo(f"❌ Label not found: {label}")
            raise typer.Exit(1)

        backuper.run(
            task,
            dry_run=dry_run,
            create_dirs=create_dirs,
        )

    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        typer.echo("Use --create-dirs option to create missing directories.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def sync(
    label: str,
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        "-f",
        help="Force create target directory if it doesn't exist",
    ),
    ssh_password: str | None = typer.Option(
        None,
        "--ssh-password",
        "-p",
        help="Password for SSH authentication (overrides .env)",
    ),
    config: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: auto-detect)"
    ),
) -> None:
    """Fetch from remote and then backup to target in a single command.

    This runs both `fetch` and `backup` tasks for the given label, if enabled.
    """
    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)

        # Get fetch task
        fetch_task = reader.config.get_task_by_label("fetch", label)
        if fetch_task and fetch_task.enabled:
            typer.echo(f"📦 Fetch {label} from {fetch_task.host} → {fetch_task.target}")
            fetcher.run(
                fetch_task,
                dry_run=dry_run,
                ssh_password=ssh_password,
                create_dirs=create_dirs,
            )
        else:
            typer.echo(f"⚠️  Skipping fetch: no enabled task found for label '{label}'")

        # Get backup task
        backup_task = reader.config.get_task_by_label("backup", label)
        if backup_task and backup_task.enabled:
            typer.echo(
                f"💾 Backup {label} from {backup_task.source} → {backup_task.target}"
            )
            backuper.run(
                backup_task,
                dry_run=dry_run,
                create_dirs=create_dirs,
            )
        else:
            typer.echo(f"⚠️  Skipping backup: no enabled task found for label '{label}'")

        typer.echo(
            f"\n✅ Sync {'preview' if dry_run else 'operation'} completed for '{label}'"
        )

    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        typer.echo("Use --create-dirs option to create missing directories.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
