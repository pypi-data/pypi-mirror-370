"""Main CLI interface for sprout."""

import typer
from rich.console import Console

from sprout import __version__
from sprout.commands.create import create_worktree
from sprout.commands.ls import list_worktrees
from sprout.commands.path import get_worktree_path
from sprout.commands.rm import remove_worktree
from sprout.types import BranchName

app = typer.Typer(
    name="sprout",
    help="CLI tool to automate git worktree and Docker Compose development workflows.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"sprout version {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """sprout - Manage git worktrees with Docker Compose environments."""
    pass


@app.command()
def create(
    branch_name: BranchName = typer.Argument(
        ...,
        help="Name of the branch to create worktree for",
    ),
    path: bool = typer.Option(
        False,
        "--path",
        help="Output only the worktree path (for use with shell command substitution)",
    ),
) -> None:
    """Create a new development environment."""
    create_worktree(branch_name, path_only=path)


@app.command()
def ls() -> None:
    """List all managed development environments."""
    list_worktrees()


@app.command()
def rm(
    identifier: str = typer.Argument(
        ...,
        help="Branch name or index number to remove",
    ),
) -> None:
    """Remove a development environment."""
    remove_worktree(identifier)


@app.command()
def path(
    identifier: str = typer.Argument(
        ...,
        help="Branch name or index number to get path for",
    ),
) -> None:
    """Get the path of a development environment."""
    get_worktree_path(identifier)


if __name__ == "__main__":
    app()
