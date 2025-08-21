"""TUI command for tvmux."""
import click

from ..tui.app import run_tui
from ..connection import Connection


@click.command()
def tui():
    """Launch the tvmux TUI interface."""
    # Ensure server is running
    conn = Connection()
    if not conn.is_running:
        click.echo("Server not running. Starting server...")
        if conn.start():
            click.echo(f"Server started at {conn.base_url}")
        else:
            click.echo("Failed to start server", err=True)
            raise click.Abort()
    
    # Launch TUI
    run_tui()


if __name__ == "__main__":
    tui()