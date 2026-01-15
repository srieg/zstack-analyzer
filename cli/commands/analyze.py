"""
Analyze command - Process Z-stack images with various algorithms
"""

import asyncio
import json
import csv
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ProcessPoolExecutor

import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich import box

from core.processing.analyzer import ZStackAnalyzer

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command("single")
def analyze_single(
    file_path: Path = typer.Argument(
        ...,
        help="Path to Z-stack image file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    algorithm: str = typer.Option(
        "segmentation_3d",
        "--algorithm",
        "-a",
        help="Analysis algorithm to use",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for results",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format (json, csv, hdf5)",
    ),
    gpu: Optional[str] = typer.Option(
        None,
        "--gpu",
        "-g",
        help="GPU device to use (e.g., 'cuda:0', 'metal')",
    ),
    threshold: float = typer.Option(
        0.5,
        "--threshold",
        "-t",
        help="Segmentation threshold (0.0-1.0)",
    ),
    min_object_size: int = typer.Option(
        100,
        "--min-object-size",
        help="Minimum object size in pixels",
    ),
) -> None:
    """
    Analyze a single Z-stack image file

    Example:
        zstack analyze single image.tif --algorithm segmentation_3d
    """

    console.print(Panel.fit(
        f"[bold cyan]Analyzing:[/bold cyan] {file_path.name}",
        box=box.ROUNDED,
    ))

    # Prepare parameters
    parameters = {
        "threshold": threshold,
        "min_object_size": min_object_size,
    }

    # Run analysis
    with console.status("[bold green]Processing...") as status:
        analyzer = ZStackAnalyzer()
        try:
            results = asyncio.run(
                analyzer.analyze(str(file_path), algorithm, parameters)
            )
        except Exception as e:
            console.print(f"[bold red]Analysis failed:[/bold red] {str(e)}")
            raise typer.Exit(1)

    # Display results
    _display_results(results)

    # Save output if requested
    if output:
        _save_results(results, output, format, file_path.stem)
        console.print(f"\n[green]✓[/green] Results saved to {output}")


@app.command("batch")
def analyze_batch(
    input_path: Path = typer.Argument(
        ...,
        help="Directory containing Z-stack images or file pattern",
        exists=True,
    ),
    algorithm: str = typer.Option(
        "segmentation_3d",
        "--algorithm",
        "-a",
        help="Analysis algorithm to use",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="Output directory for results",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format (json, csv, hdf5)",
    ),
    parallel: int = typer.Option(
        4,
        "--parallel",
        "-p",
        help="Number of parallel workers",
        min=1,
        max=32,
    ),
    gpu: Optional[str] = typer.Option(
        None,
        "--gpu",
        "-g",
        help="GPU device to use",
    ),
    pattern: str = typer.Option(
        "*.tif",
        "--pattern",
        help="File pattern to match (e.g., '*.tif', '*.czi')",
    ),
    threshold: float = typer.Option(
        0.5,
        "--threshold",
        "-t",
        help="Segmentation threshold",
    ),
    min_object_size: int = typer.Option(
        100,
        "--min-object-size",
        help="Minimum object size in pixels",
    ),
) -> None:
    """
    Batch analyze multiple Z-stack images

    Example:
        zstack analyze batch ./data/ --output ./results/ --parallel 8
    """

    # Find files to process
    if input_path.is_dir():
        files = sorted(input_path.glob(pattern))
    else:
        files = [input_path]

    if not files:
        console.print(f"[bold red]No files found matching pattern: {pattern}[/bold red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]Found {len(files)} files to process[/bold cyan]\n")

    # Create output directory
    output.mkdir(parents=True, exist_ok=True)

    # Prepare parameters
    parameters = {
        "threshold": threshold,
        "min_object_size": min_object_size,
    }

    # Process files with progress bar
    results_list = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task(
            f"[cyan]Processing with {algorithm}...",
            total=len(files)
        )

        analyzer = ZStackAnalyzer()

        for file_path in files:
            progress.update(task, description=f"[cyan]Processing {file_path.name}...")

            try:
                result = asyncio.run(
                    analyzer.analyze(str(file_path), algorithm, parameters)
                )
                result["file_path"] = str(file_path)
                results_list.append(result)

                # Save individual result
                _save_results(result, output, format, file_path.stem)

            except Exception as e:
                console.print(f"[yellow]⚠️  Failed to process {file_path.name}: {str(e)}[/yellow]")

            progress.advance(task)

    # Display summary
    _display_batch_summary(results_list, algorithm)

    # Save combined results
    if format == "csv":
        _save_batch_csv(results_list, output / f"batch_results_{algorithm}.csv")
        console.print(f"\n[green]✓[/green] Batch results saved to {output / f'batch_results_{algorithm}.csv'}")


def _display_results(results: dict) -> None:
    """Display analysis results in a formatted table"""

    table = Table(title="Analysis Results", box=box.ROUNDED)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Algorithm", results["algorithm"])
    table.add_row("Version", results["version"])
    table.add_row("GPU Device", str(results.get("gpu_device", "CPU")))
    table.add_row("Processing Time", f"{results['processing_time_ms']} ms")
    table.add_row("Confidence Score", f"{results.get('confidence_score', 0.0):.2f}")

    # Add algorithm-specific results
    for key, value in results.get("results", {}).items():
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                table.add_row(key.replace("_", " ").title(), f"{value:.4f}")
            else:
                table.add_row(key.replace("_", " ").title(), str(value))

    console.print("\n")
    console.print(table)


def _display_batch_summary(results_list: List[dict], algorithm: str) -> None:
    """Display summary of batch processing"""

    if not results_list:
        console.print("[yellow]No results to display[/yellow]")
        return

    total_files = len(results_list)
    total_time = sum(r["processing_time_ms"] for r in results_list)
    avg_time = total_time / total_files
    avg_confidence = sum(r.get("confidence_score", 0.0) for r in results_list) / total_files

    table = Table(title="Batch Processing Summary", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Files Processed", str(total_files))
    table.add_row("Algorithm", algorithm)
    table.add_row("Total Processing Time", f"{total_time / 1000:.2f} seconds")
    table.add_row("Average Time per File", f"{avg_time:.0f} ms")
    table.add_row("Average Confidence", f"{avg_confidence:.2f}")

    console.print("\n")
    console.print(table)


def _save_results(results: dict, output: Path, format: str, filename: str) -> None:
    """Save results in specified format"""

    output.mkdir(parents=True, exist_ok=True)

    if format == "json":
        output_file = output / f"{filename}_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

    elif format == "csv":
        output_file = output / f"{filename}_results.csv"
        # Flatten results for CSV
        flat_results = _flatten_dict(results)
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=flat_results.keys())
            writer.writeheader()
            writer.writerow(flat_results)

    elif format == "hdf5":
        console.print("[yellow]HDF5 format not yet implemented, saving as JSON[/yellow]")
        _save_results(results, output, "json", filename)


def _save_batch_csv(results_list: List[dict], output_file: Path) -> None:
    """Save batch results to a single CSV file"""

    if not results_list:
        return

    # Flatten all results
    flat_results = [_flatten_dict(r) for r in results_list]

    # Get all unique keys
    all_keys = set()
    for result in flat_results:
        all_keys.update(result.keys())

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(flat_results)


def _flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v)))
        else:
            items.append((new_key, v))
    return dict(items)


@app.command("list-algorithms")
def list_algorithms() -> None:
    """
    List all available analysis algorithms
    """

    analyzer = ZStackAnalyzer()
    algorithms = list(analyzer.available_algorithms.keys())

    table = Table(title="Available Algorithms", box=box.ROUNDED)
    table.add_column("Algorithm", style="cyan")
    table.add_column("Description", style="white")

    descriptions = {
        "segmentation_3d": "3D cell segmentation using deep learning",
        "colocalization": "Multi-channel colocalization analysis",
        "intensity_analysis": "Intensity statistics and distribution",
        "deconvolution": "Richardson-Lucy deconvolution",
    }

    for algo in algorithms:
        table.add_row(algo, descriptions.get(algo, "No description available"))

    console.print("\n")
    console.print(table)


if __name__ == "__main__":
    app()
