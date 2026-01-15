"""
Info command - Display file metadata and quick preview stats
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.columns import Columns
from rich.text import Text

from core.processing.image_loader import ImageLoader

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command()
def show(
    file_path: Path = typer.Argument(
        ...,
        help="Path to Z-stack image file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed metadata",
    ),
) -> None:
    """
    Show file metadata and information

    Example:
        zstack info image.tif
        zstack info image.tif --verbose
    """

    console.print(f"\n[bold cyan]Analyzing file:[/bold cyan] {file_path.name}\n")

    # Load metadata
    loader = ImageLoader()
    try:
        with console.status("[bold green]Loading metadata..."):
            metadata = asyncio.run(loader.get_metadata(str(file_path)))
    except Exception as e:
        console.print(f"[bold red]Failed to load metadata:[/bold red] {str(e)}")
        raise typer.Exit(1)

    # Display basic info
    _display_basic_info(file_path, metadata)

    # Display dimensional info
    _display_dimensions(metadata)

    # Display acquisition info
    _display_acquisition_info(metadata)

    # Display channel info
    _display_channel_info(metadata)

    # Display verbose info if requested
    if verbose and metadata.get("custom_metadata"):
        _display_custom_metadata(metadata["custom_metadata"])


def _display_basic_info(file_path: Path, metadata: dict) -> None:
    """Display basic file information"""

    file_size = metadata.get("file_size", 0)
    file_size_mb = file_size / (1024 * 1024)

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("📄 Filename", metadata.get("filename", file_path.name))
    table.add_row("📦 File Size", f"{file_size_mb:.2f} MB")
    table.add_row("📁 Format", file_path.suffix.upper())
    table.add_row("🔢 Bit Depth", f"{metadata.get('bit_depth', 'Unknown')} bits")

    console.print(Panel(table, title="[bold]File Information[/bold]", box=box.ROUNDED))


def _display_dimensions(metadata: dict) -> None:
    """Display image dimensions"""

    width = metadata.get("width", 0)
    height = metadata.get("height", 0)
    depth = metadata.get("depth", 0)
    channels = metadata.get("channels", 1)

    # Calculate volume in voxels
    total_voxels = width * height * depth * channels
    total_voxels_m = total_voxels / 1_000_000

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Dimension", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Width (X)", f"{width:,} px")
    table.add_row("Height (Y)", f"{height:,} px")
    table.add_row("Depth (Z)", f"{depth:,} slices")
    table.add_row("Channels", str(channels))
    table.add_row("Total Voxels", f"{total_voxels_m:.2f}M")

    console.print(Panel(table, title="[bold]Dimensions[/bold]", box=box.ROUNDED))


def _display_acquisition_info(metadata: dict) -> None:
    """Display acquisition parameters"""

    pixel_size_x = metadata.get("pixel_size_x", 0)
    pixel_size_y = metadata.get("pixel_size_y", 0)
    pixel_size_z = metadata.get("pixel_size_z", 0)

    # Calculate physical dimensions in micrometers
    width_um = metadata.get("width", 0) * pixel_size_x if pixel_size_x else 0
    height_um = metadata.get("height", 0) * pixel_size_y if pixel_size_y else 0
    depth_um = metadata.get("depth", 0) * pixel_size_z if pixel_size_z else 0

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="white")

    if pixel_size_x and pixel_size_y:
        table.add_row("Pixel Size (XY)", f"{pixel_size_x:.3f} × {pixel_size_y:.3f} µm")
        table.add_row("Physical Size (XY)", f"{width_um:.1f} × {height_um:.1f} µm")

    if pixel_size_z:
        table.add_row("Z-Step Size", f"{pixel_size_z:.3f} µm")
        table.add_row("Physical Depth", f"{depth_um:.1f} µm")

    microscope = metadata.get("microscope_info")
    if microscope:
        table.add_row("Microscope", str(microscope))

    objective = metadata.get("objective_info")
    if objective:
        table.add_row("Objective", str(objective))

    acq_date = metadata.get("acquisition_date")
    if acq_date:
        table.add_row("Acquisition Date", str(acq_date))

    if table.row_count > 0:
        console.print(Panel(table, title="[bold]Acquisition Info[/bold]", box=box.ROUNDED))


def _display_channel_info(metadata: dict) -> None:
    """Display channel information"""

    channels = metadata.get("channels", 1)
    channel_names = metadata.get("channel_names", [])
    exposure_times = metadata.get("exposure_times", [])

    if channels == 1 and not channel_names:
        return

    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("Channel", style="cyan", justify="center")
    table.add_column("Name", style="white")
    table.add_column("Exposure (ms)", style="green", justify="right")

    for i in range(channels):
        channel_num = i + 1
        name = channel_names[i] if i < len(channel_names) else f"Channel {channel_num}"
        exposure = exposure_times[i] if i < len(exposure_times) else "N/A"

        if isinstance(exposure, (int, float)):
            exposure = f"{exposure:.1f}"

        table.add_row(str(channel_num), name, str(exposure))

    console.print(Panel(table, title="[bold]Channels[/bold]", box=box.ROUNDED))


def _display_custom_metadata(custom_metadata: dict) -> None:
    """Display custom metadata fields"""

    if not custom_metadata:
        return

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    for key, value in custom_metadata.items():
        table.add_row(key, str(value))

    console.print(Panel(table, title="[bold]Custom Metadata[/bold]", box=box.ROUNDED))


@app.command("batch")
def batch_info(
    input_path: Path = typer.Argument(
        ...,
        help="Directory containing Z-stack images",
        exists=True,
        dir_okay=True,
    ),
    pattern: str = typer.Option(
        "*.tif",
        "--pattern",
        help="File pattern to match",
    ),
) -> None:
    """
    Show summary information for multiple files

    Example:
        zstack info batch ./data/ --pattern "*.tif"
    """

    # Find files
    files = sorted(input_path.glob(pattern))

    if not files:
        console.print(f"[bold red]No files found matching pattern: {pattern}[/bold red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]Found {len(files)} files[/bold cyan]\n")

    # Load metadata for all files
    loader = ImageLoader()
    metadata_list = []

    for file_path in files:
        try:
            metadata = asyncio.run(loader.get_metadata(str(file_path)))
            metadata["filename"] = file_path.name
            metadata_list.append(metadata)
        except Exception as e:
            console.print(f"[yellow]⚠️  Failed to load {file_path.name}: {str(e)}[/yellow]")

    # Display summary table
    _display_batch_summary(metadata_list)


def _display_batch_summary(metadata_list: list) -> None:
    """Display summary table for batch info"""

    if not metadata_list:
        console.print("[yellow]No metadata to display[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Size (MB)", style="white", justify="right")
    table.add_column("Dimensions", style="green", justify="center")
    table.add_column("Channels", style="yellow", justify="center")
    table.add_column("Bit Depth", style="magenta", justify="center")

    for metadata in metadata_list:
        filename = metadata.get("filename", "Unknown")
        file_size = metadata.get("file_size", 0) / (1024 * 1024)
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)
        depth = metadata.get("depth", 0)
        channels = metadata.get("channels", 1)
        bit_depth = metadata.get("bit_depth", "?")

        dimensions = f"{width}×{height}×{depth}"

        table.add_row(
            filename[:30],
            f"{file_size:.1f}",
            dimensions,
            str(channels),
            str(bit_depth),
        )

    console.print(table)


if __name__ == "__main__":
    app()
