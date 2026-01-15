"""
Z-Stack Analyzer CLI Entry Point

Usage: python -m cli <command> [options]
       zstack <command> [options]  (after installation)
"""

import typer
from typing import Optional
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel

# Import commands
from cli.commands import analyze, info, convert, benchmark, serve

console = Console()

app = typer.Typer(
    name="zstack",
    help="🔬 Z-Stack Analyzer - GPU-accelerated confocal microscopy analysis",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Register commands
app.add_typer(analyze.app, name="analyze", help="🧬 Analyze Z-stack images")
app.add_typer(info.app, name="info", help="ℹ️  Show file metadata and information")
app.add_typer(convert.app, name="convert", help="🔄 Convert between file formats")
app.add_typer(benchmark.app, name="benchmark", help="⚡ Run performance benchmarks")
app.add_typer(serve.app, name="serve", help="🌐 Start the web server")


@app.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        is_eager=True,
    ),
) -> None:
    """
    Z-Stack Analyzer - GPU-accelerated confocal microscopy analysis
    """
    if version:
        from cli import __version__
        console.print(f"[bold cyan]Z-Stack Analyzer[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


def cli_entry() -> None:
    """Entry point for installed CLI"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli_entry()
