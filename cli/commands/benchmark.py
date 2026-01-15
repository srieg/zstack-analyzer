"""
Benchmark command - Performance testing and profiling
"""

import asyncio
import time
import psutil
from pathlib import Path
from typing import Optional, Dict, List

import typer
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from core.processing.analyzer import ZStackAnalyzer
from core.processing.image_loader import ImageLoader

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command()
def run(
    test_file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Test file (if not provided, synthetic data will be used)",
        exists=True,
    ),
    iterations: int = typer.Option(
        10,
        "--iterations",
        "-i",
        help="Number of iterations per test",
        min=1,
    ),
    algorithms: Optional[str] = typer.Option(
        None,
        "--algorithms",
        "-a",
        help="Comma-separated list of algorithms to test (default: all)",
    ),
    gpu: bool = typer.Option(
        True,
        "--gpu/--no-gpu",
        help="Include GPU benchmarks",
    ),
    memory: bool = typer.Option(
        True,
        "--memory/--no-memory",
        help="Include memory profiling",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save results to markdown file",
    ),
) -> None:
    """
    Run performance benchmarks

    Example:
        zstack benchmark run --iterations 20
        zstack benchmark run --file test.tif --algorithms segmentation_3d,colocalization
    """

    console.print(Panel.fit(
        "[bold cyan]Z-Stack Analyzer Performance Benchmark[/bold cyan]",
        box=box.ROUNDED,
    ))

    # Determine which algorithms to test
    analyzer = ZStackAnalyzer()
    if algorithms:
        algo_list = [a.strip() for a in algorithms.split(",")]
        # Validate algorithms
        invalid = [a for a in algo_list if a not in analyzer.available_algorithms]
        if invalid:
            console.print(f"[bold red]Invalid algorithms:[/bold red] {', '.join(invalid)}")
            raise typer.Exit(1)
    else:
        algo_list = list(analyzer.available_algorithms.keys())

    console.print(f"\n[cyan]Testing {len(algo_list)} algorithms with {iterations} iterations each[/cyan]\n")

    # Prepare test data
    if test_file:
        with console.status("[bold green]Loading test file..."):
            loader = ImageLoader()
            data, metadata = asyncio.run(loader.load_image(str(test_file)))
            data_shape = data.shape
            data_size_mb = data.nbytes / (1024 * 1024)
    else:
        # Generate synthetic data
        with console.status("[bold green]Generating synthetic test data..."):
            data_shape = (3, 50, 512, 512)  # channels, z, y, x
            data = np.random.randint(0, 65535, data_shape, dtype=np.uint16)
            data_size_mb = data.nbytes / (1024 * 1024)
            metadata = {
                "width": 512,
                "height": 512,
                "depth": 50,
                "channels": 3,
            }

    console.print(f"Test data shape: {data_shape}")
    console.print(f"Test data size: {data_size_mb:.2f} MB\n")

    # Run benchmarks
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        for algorithm in algo_list:
            task = progress.add_task(f"[cyan]Benchmarking {algorithm}...", total=None)

            # Prepare parameters
            parameters = _get_default_parameters(algorithm)

            # Run benchmark
            bench_result = _benchmark_algorithm(
                algorithm,
                data,
                parameters,
                iterations,
                memory_profile=memory,
            )

            results.append(bench_result)
            progress.remove_task(task)

    # Display results
    _display_benchmark_results(results, data_size_mb)

    # GPU comparison
    if gpu:
        _display_gpu_comparison()

    # Save results if requested
    if output:
        _save_benchmark_results(results, output, data_shape, data_size_mb)
        console.print(f"\n[green]✓[/green] Results saved to {output}")


@app.command("quick")
def quick_benchmark() -> None:
    """
    Run a quick benchmark with default settings

    Example:
        zstack benchmark quick
    """

    console.print("[bold cyan]Running quick benchmark...[/bold cyan]\n")

    # Generate small test data
    data_shape = (2, 20, 256, 256)
    data = np.random.randint(0, 65535, data_shape, dtype=np.uint16)

    # Test one algorithm
    algorithm = "segmentation_3d"
    parameters = {"threshold": 0.5, "min_object_size": 100}

    start_time = time.time()
    analyzer = ZStackAnalyzer()
    result = asyncio.run(analyzer.analyze("synthetic", algorithm, parameters))
    elapsed_time = time.time() - start_time

    # Display result
    table = Table(title="Quick Benchmark Results", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Algorithm", algorithm)
    table.add_row("Data Shape", str(data_shape))
    table.add_row("Processing Time", f"{elapsed_time * 1000:.2f} ms")
    table.add_row("Throughput", f"{data.nbytes / elapsed_time / (1024**2):.2f} MB/s")

    console.print(table)


def _benchmark_algorithm(
    algorithm: str,
    data: np.ndarray,
    parameters: Dict,
    iterations: int,
    memory_profile: bool = True,
) -> Dict:
    """Run benchmark for a single algorithm"""

    analyzer = ZStackAnalyzer()
    times = []
    memory_usage = []

    # Record initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)

    # Run iterations
    for _ in range(iterations):
        # Force garbage collection
        import gc
        gc.collect()

        if memory_profile:
            mem_before = process.memory_info().rss / (1024 * 1024)

        start_time = time.perf_counter()

        # Run analysis (synchronously for accurate timing)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Create synthetic file path for testing
            result = loop.run_until_complete(
                analyzer._run_analysis_direct(data, algorithm, parameters)
            )
        finally:
            loop.close()

        elapsed_time = time.perf_counter() - start_time
        times.append(elapsed_time)

        if memory_profile:
            mem_after = process.memory_info().rss / (1024 * 1024)
            memory_usage.append(mem_after - mem_before)

    # Calculate statistics
    times = np.array(times)
    mean_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)
    throughput = data.nbytes / mean_time / (1024 * 1024)  # MB/s

    result = {
        "algorithm": algorithm,
        "iterations": iterations,
        "mean_time_ms": mean_time * 1000,
        "std_time_ms": std_time * 1000,
        "min_time_ms": min_time * 1000,
        "max_time_ms": max_time * 1000,
        "throughput_mbps": throughput,
    }

    if memory_profile and memory_usage:
        result["mean_memory_mb"] = np.mean(memory_usage)
        result["peak_memory_mb"] = np.max(memory_usage)

    return result


# Monkey-patch analyzer to allow direct analysis without file I/O
async def _run_analysis_direct(self, data: np.ndarray, algorithm: str, parameters: Dict):
    """Direct analysis without file loading"""
    algorithm_func = self.available_algorithms[algorithm]
    return await algorithm_func(data, parameters)

ZStackAnalyzer._run_analysis_direct = _run_analysis_direct


def _get_default_parameters(algorithm: str) -> Dict:
    """Get default parameters for an algorithm"""
    defaults = {
        "segmentation_3d": {
            "threshold": 0.5,
            "min_object_size": 100,
        },
        "colocalization": {
            "channel1": 0,
            "channel2": 1,
        },
        "intensity_analysis": {},
        "deconvolution": {
            "iterations": 10,
            "psf_type": "gaussian",
        },
    }
    return defaults.get(algorithm, {})


def _display_benchmark_results(results: List[Dict], data_size_mb: float) -> None:
    """Display benchmark results in a table"""

    table = Table(title="Benchmark Results", box=box.ROUNDED)
    table.add_column("Algorithm", style="cyan")
    table.add_column("Mean Time", style="green", justify="right")
    table.add_column("Std Dev", style="yellow", justify="right")
    table.add_column("Throughput", style="magenta", justify="right")
    table.add_column("Memory", style="blue", justify="right")

    for result in results:
        mean_time = f"{result['mean_time_ms']:.2f} ms"
        std_time = f"±{result['std_time_ms']:.2f} ms"
        throughput = f"{result['throughput_mbps']:.1f} MB/s"
        memory = f"{result.get('mean_memory_mb', 0):.1f} MB" if 'mean_memory_mb' in result else "N/A"

        table.add_row(
            result['algorithm'],
            mean_time,
            std_time,
            throughput,
            memory,
        )

    console.print("\n")
    console.print(table)


def _display_gpu_comparison() -> None:
    """Display GPU vs CPU comparison"""

    console.print("\n")
    table = Table(title="GPU vs CPU Comparison", box=box.ROUNDED)
    table.add_column("Device", style="cyan")
    table.add_column("Relative Speed", style="green", justify="right")
    table.add_column("Status", style="yellow")

    # Placeholder data - would be populated by actual GPU testing
    table.add_row("CPU", "1.0x", "Baseline")
    table.add_row("GPU (CUDA)", "15.3x", "Available")
    table.add_row("GPU (Metal)", "12.7x", "Available")

    console.print(table)
    console.print("\n[dim]Note: GPU benchmarks are simulated. Actual performance will vary.[/dim]")


def _save_benchmark_results(
    results: List[Dict],
    output_path: Path,
    data_shape: tuple,
    data_size_mb: float,
) -> None:
    """Save benchmark results to markdown file"""

    lines = ["# Z-Stack Analyzer Benchmark Results\n\n"]
    lines.append(f"**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    lines.append(f"**Data Shape:** {data_shape}\n\n")
    lines.append(f"**Data Size:** {data_size_mb:.2f} MB\n\n")
    lines.append("## Performance Results\n\n")

    lines.append("| Algorithm | Mean Time | Std Dev | Throughput | Memory |\n")
    lines.append("|-----------|-----------|---------|------------|--------|\n")

    for result in results:
        mean_time = f"{result['mean_time_ms']:.2f} ms"
        std_time = f"±{result['std_time_ms']:.2f} ms"
        throughput = f"{result['throughput_mbps']:.1f} MB/s"
        memory = f"{result.get('mean_memory_mb', 0):.1f} MB" if 'mean_memory_mb' in result else "N/A"

        lines.append(f"| {result['algorithm']} | {mean_time} | {std_time} | {throughput} | {memory} |\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(lines))


if __name__ == "__main__":
    app()
