"""Ties CLI entry point to duplicate and sync file content with advanced transformations.."""

import typer

from ._configuration import load_config
from ._consts import ERROR, SUCCESS, Colors, cprint
from ._file_processing import process_files

app = typer.Typer(
    rich_markup_mode="rich",
    help="""[bold green]A tool to keep files in sync within a repository.[/bold green]

Use with pre-commit to enforce file content consistency.""",
)


def _run_command(command: str) -> None:
    config = load_config()
    if not config or "tie" not in config:
        cprint(
            "❌ Error: No configuration found in ties.toml or pyproject.toml under [tool.ties].",
            Colors.RED,
            bold=True,
        )
        cprint("Please ensure you have a [[tool.ties.tie]] section.", Colors.CYAN)
        raise typer.Exit(ERROR)
    if not process_files(config, command):
        raise typer.Exit(ERROR)
    raise typer.Exit(SUCCESS)


@app.command(help="Check for discrepancies and exit with an error if any are found.")
def check() -> None:
    """Check for discrepancies."""
    _run_command("check")


@app.command(help="Automatically fix discrepancies by overwriting target files.")
def fix() -> None:
    """Automatically fix discrepancies."""
    _run_command("fix")


if __name__ == "__main__":
    app()
