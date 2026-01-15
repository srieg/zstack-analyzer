"""
Serve command - Start the web server
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command()
def start(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to bind to",
        min=1,
        max=65535,
    ),
    workers: int = typer.Option(
        4,
        "--workers",
        "-w",
        help="Number of worker processes",
        min=1,
        max=32,
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
    log_level: str = typer.Option(
        "info",
        "--log-level",
        "-l",
        help="Log level (debug, info, warning, error)",
    ),
) -> None:
    """
    Start the Z-Stack Analyzer web server

    Example:
        zstack serve start
        zstack serve start --port 8080 --workers 8
        zstack serve start --reload  # Development mode
    """

    console.print(Panel.fit(
        "[bold cyan]Starting Z-Stack Analyzer Web Server[/bold cyan]",
        box=box.ROUNDED,
    ))

    console.print(f"\n[cyan]Configuration:[/cyan]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print(f"  Workers: {workers}")
    console.print(f"  Reload: {'enabled' if reload else 'disabled'}")
    console.print(f"  Log Level: {log_level}")
    console.print()

    # Build uvicorn command
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", log_level,
    ]

    if reload:
        cmd.append("--reload")
    else:
        cmd.extend(["--workers", str(workers)])

    console.print(f"[dim]Command: {' '.join(cmd)}[/dim]\n")

    # Display access URLs
    console.print("[bold green]Server starting...[/bold green]\n")
    console.print(f"[cyan]→[/cyan] API: http://localhost:{port}")
    console.print(f"[cyan]→[/cyan] Docs: http://localhost:{port}/docs")
    console.print(f"[cyan]→[/cyan] Health: http://localhost:{port}/health")
    console.print()
    console.print("[dim]Press CTRL+C to stop the server[/dim]\n")

    # Start server
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]Server failed to start:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """
    Check if the server is running

    Example:
        zstack serve status
    """

    import requests

    default_port = 8000
    url = f"http://localhost:{default_port}/health"

    console.print(f"[cyan]Checking server at {url}...[/cyan]\n")

    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            console.print("[bold green]✓[/bold green] Server is running")
            console.print(f"  Status: {data.get('status', 'unknown')}")
            console.print(f"  Service: {data.get('service', 'unknown')}")
        else:
            console.print(f"[yellow]⚠️  Server responded with status {response.status_code}[/yellow]")
    except requests.exceptions.ConnectionError:
        console.print("[bold red]✗[/bold red] Server is not running")
        console.print(f"  No server found at port {default_port}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command()
def dev() -> None:
    """
    Start server in development mode (with auto-reload)

    Example:
        zstack serve dev
    """

    console.print("[bold cyan]Starting development server...[/bold cyan]\n")

    start(
        host="127.0.0.1",
        port=8000,
        workers=1,
        reload=True,
        log_level="debug",
    )


@app.command()
def prod() -> None:
    """
    Start server in production mode

    Example:
        zstack serve prod
    """

    import multiprocessing

    # Use number of CPU cores for workers
    workers = multiprocessing.cpu_count()

    console.print("[bold cyan]Starting production server...[/bold cyan]\n")

    start(
        host="0.0.0.0",
        port=8000,
        workers=workers,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    app()
