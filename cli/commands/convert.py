"""
Convert command - Convert between image formats
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich import box

from core.processing.image_loader import ImageLoader

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command()
def convert(
    input_path: Path = typer.Argument(
        ...,
        help="Input image file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output_path: Path = typer.Argument(
        ...,
        help="Output image file",
    ),
    compression: Optional[str] = typer.Option(
        None,
        "--compression",
        "-c",
        help="Compression method (none, lzw, zip, jpeg)",
    ),
    quality: int = typer.Option(
        95,
        "--quality",
        "-q",
        help="Compression quality (1-100, for lossy formats)",
        min=1,
        max=100,
    ),
    bit_depth: Optional[int] = typer.Option(
        None,
        "--bit-depth",
        "-b",
        help="Output bit depth (8, 16, 32)",
    ),
) -> None:
    """
    Convert between image formats

    Supported formats:
    - TIFF (.tif, .tiff)
    - OME-TIFF (.ome.tif, .ome.tiff)
    - HDF5 (.h5, .hdf5)
    - Zarr (.zarr)

    Example:
        zstack convert input.tif output.ome.tif --compression lzw
        zstack convert input.czi output.h5 --bit-depth 16
    """

    console.print(Panel.fit(
        f"[bold cyan]Converting:[/bold cyan] {input_path.name} → {output_path.name}",
        box=box.ROUNDED,
    ))

    # Validate formats
    input_ext = input_path.suffix.lower()
    output_ext = output_path.suffix.lower()

    supported_input = {'.tif', '.tiff', '.czi', '.nd2', '.lsm'}
    supported_output = {'.tif', '.tiff', '.h5', '.hdf5', '.zarr'}

    if input_ext not in supported_input:
        console.print(f"[bold red]Unsupported input format:[/bold red] {input_ext}")
        raise typer.Exit(1)

    if output_ext not in supported_output:
        console.print(f"[bold red]Unsupported output format:[/bold red] {output_ext}")
        raise typer.Exit(1)

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Perform conversion
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("[cyan]Loading image...", total=100)

        try:
            # Load input image
            loader = ImageLoader()
            data, metadata = asyncio.run(loader.load_image(str(input_path)))
            progress.update(task, advance=30, description="[cyan]Processing...")

            # Convert bit depth if requested
            if bit_depth:
                data = _convert_bit_depth(data, bit_depth)
                progress.update(task, advance=20)

            # Save output
            progress.update(task, description="[cyan]Saving output...")
            _save_image(data, metadata, output_path, compression, quality)
            progress.update(task, advance=50, description="[green]Complete!")

        except NotImplementedError as e:
            console.print(f"\n[bold red]Conversion not yet implemented:[/bold red] {str(e)}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n[bold red]Conversion failed:[/bold red] {str(e)}")
            raise typer.Exit(1)

    # Display result
    input_size = input_path.stat().st_size / (1024 * 1024)
    output_size = output_path.stat().st_size / (1024 * 1024)
    compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0

    console.print(f"\n[green]✓[/green] Conversion complete!")
    console.print(f"  Input size:  {input_size:.2f} MB")
    console.print(f"  Output size: {output_size:.2f} MB")
    if compression_ratio > 0:
        console.print(f"  Compression: {compression_ratio:.1f}% reduction")


@app.command("batch")
def batch_convert(
    input_path: Path = typer.Argument(
        ...,
        help="Input directory",
        exists=True,
        dir_okay=True,
    ),
    output_path: Path = typer.Argument(
        ...,
        help="Output directory",
    ),
    output_format: str = typer.Option(
        ...,
        "--format",
        "-f",
        help="Output format (tif, ome.tif, h5, zarr)",
    ),
    pattern: str = typer.Option(
        "*.tif",
        "--pattern",
        help="Input file pattern",
    ),
    compression: Optional[str] = typer.Option(
        None,
        "--compression",
        "-c",
        help="Compression method",
    ),
) -> None:
    """
    Batch convert multiple files

    Example:
        zstack convert batch ./input/ ./output/ --format ome.tif --pattern "*.czi"
    """

    # Find input files
    files = sorted(input_path.glob(pattern))

    if not files:
        console.print(f"[bold red]No files found matching pattern: {pattern}[/bold red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]Converting {len(files)} files to {output_format}[/bold cyan]\n")

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Process files
    loader = ImageLoader()
    success_count = 0
    failed_count = 0

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Converting...", total=len(files))

        for file_path in files:
            try:
                # Load image
                data, metadata = asyncio.run(loader.load_image(str(file_path)))

                # Generate output filename
                output_file = output_path / f"{file_path.stem}.{output_format}"

                # Save
                _save_image(data, metadata, output_file, compression, quality=95)

                success_count += 1

            except Exception as e:
                console.print(f"[yellow]⚠️  Failed to convert {file_path.name}: {str(e)}[/yellow]")
                failed_count += 1

            progress.advance(task)

    console.print(f"\n[green]✓[/green] Batch conversion complete!")
    console.print(f"  Successful: {success_count}")
    if failed_count > 0:
        console.print(f"  Failed: {failed_count}")


def _convert_bit_depth(data, target_bit_depth: int):
    """Convert image bit depth"""
    import numpy as np

    current_dtype = data.dtype
    current_max = np.iinfo(current_dtype).max if np.issubdtype(current_dtype, np.integer) else 1.0

    if target_bit_depth == 8:
        target_dtype = np.uint8
        target_max = 255
    elif target_bit_depth == 16:
        target_dtype = np.uint16
        target_max = 65535
    elif target_bit_depth == 32:
        target_dtype = np.float32
        return data.astype(target_dtype) / current_max
    else:
        raise ValueError(f"Unsupported bit depth: {target_bit_depth}")

    # Scale data
    scaled = (data.astype(np.float64) / current_max * target_max).astype(target_dtype)
    return scaled


def _save_image(data, metadata: dict, output_path: Path, compression: Optional[str], quality: int) -> None:
    """Save image to file"""
    from skimage import io
    import numpy as np

    output_ext = output_path.suffix.lower()

    if output_ext in {'.tif', '.tiff'}:
        # Save as TIFF
        compress_map = {
            'none': 0,
            'lzw': 5,
            'zip': 8,
            'jpeg': 7,
        }

        compress_level = compress_map.get(compression, 0) if compression else 0

        # Use skimage for TIFF saving
        io.imsave(str(output_path), data, check_contrast=False)

    elif output_ext in {'.h5', '.hdf5'}:
        # HDF5 format
        raise NotImplementedError("HDF5 output not yet implemented. Please install h5py and implement _save_hdf5()")

    elif output_ext == '.zarr':
        # Zarr format
        raise NotImplementedError("Zarr output not yet implemented. Please install zarr and implement _save_zarr()")

    else:
        raise ValueError(f"Unsupported output format: {output_ext}")


if __name__ == "__main__":
    app()
