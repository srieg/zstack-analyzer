#!/usr/bin/env python3
"""
Z-Stack Analyzer Pipeline Example

This script demonstrates how to build a custom analysis pipeline
using the Z-Stack Analyzer as a Python library.

Example usage:
    python pipeline.py --input ./data/ --output ./results/
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table

# Import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.processing.analyzer import ZStackAnalyzer
from core.processing.image_loader import ImageLoader

console = Console()


class AnalysisPipeline:
    """Custom analysis pipeline for Z-stack images"""

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.analyzer = ZStackAnalyzer()
        self.loader = ImageLoader()
        self.results = []

    async def run(self) -> None:
        """Execute the complete analysis pipeline"""

        console.print(Panel.fit(
            "[bold cyan]Z-Stack Analysis Pipeline[/bold cyan]",
            subtitle="Custom Multi-Algorithm Pipeline"
        ))

        # Step 1: Discover files
        files = self._discover_files()
        console.print(f"\n[cyan]Step 1:[/cyan] Found {len(files)} files to process\n")

        if not files:
            console.print("[yellow]No files found. Exiting.[/yellow]")
            return

        # Step 2: Quality control
        console.print("[cyan]Step 2:[/cyan] Quality control")
        quality_passed = await self._quality_control(files)
        console.print(f"  ✓ {len(quality_passed)}/{len(files)} files passed QC\n")

        # Step 3: Run multiple algorithms
        console.print("[cyan]Step 3:[/cyan] Running analysis algorithms")
        await self._run_multi_algorithm_analysis(quality_passed)

        # Step 4: Post-processing
        console.print("\n[cyan]Step 4:[/cyan] Post-processing and aggregation")
        self._post_process_results()

        # Step 5: Generate reports
        console.print("[cyan]Step 5:[/cyan] Generating reports")
        self._generate_reports()

        console.print("\n[bold green]✓ Pipeline complete![/bold green]")

    def _discover_files(self) -> List[Path]:
        """Discover Z-stack image files"""
        patterns = ["*.tif", "*.tiff", "*.czi"]
        files = []
        for pattern in patterns:
            files.extend(self.input_dir.glob(pattern))
        return sorted(files)

    async def _quality_control(self, files: List[Path]) -> List[Path]:
        """Perform quality control checks on files"""

        passed = []
        failed = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:

            task = progress.add_task("[cyan]Running QC checks...", total=len(files))

            for file_path in files:
                try:
                    # Load metadata
                    metadata = await self.loader.get_metadata(str(file_path))

                    # QC checks
                    if metadata.get("width", 0) < 256:
                        failed.append((file_path, "Image too small"))
                        continue

                    if metadata.get("depth", 0) < 5:
                        failed.append((file_path, "Not enough Z-slices"))
                        continue

                    passed.append(file_path)

                except Exception as e:
                    failed.append((file_path, str(e)))

                progress.advance(task)

        if failed:
            console.print("\n[yellow]QC Failures:[/yellow]")
            for file_path, reason in failed:
                console.print(f"  ⚠️  {file_path.name}: {reason}")

        return passed

    async def _run_multi_algorithm_analysis(self, files: List[Path]) -> None:
        """Run multiple analysis algorithms on each file"""

        algorithms = [
            ("segmentation_3d", {"threshold": 0.5, "min_object_size": 100}),
            ("intensity_analysis", {}),
            ("colocalization", {"channel1": 0, "channel2": 1}),
        ]

        total_tasks = len(files) * len(algorithms)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:

            task = progress.add_task(
                "[cyan]Processing...",
                total=total_tasks
            )

            for file_path in files:
                file_results = {
                    "file": str(file_path),
                    "algorithms": {}
                }

                for algorithm, params in algorithms:
                    try:
                        result = await self.analyzer.analyze(
                            str(file_path),
                            algorithm,
                            params
                        )
                        file_results["algorithms"][algorithm] = result

                    except Exception as e:
                        console.print(f"[yellow]⚠️  {file_path.name} - {algorithm} failed: {str(e)}[/yellow]")

                    progress.advance(task)

                self.results.append(file_results)

    def _post_process_results(self) -> None:
        """Post-process and aggregate results"""

        # Calculate summary statistics
        total_objects = 0
        total_processing_time = 0

        for file_result in self.results:
            for algo, result in file_result["algorithms"].items():
                total_processing_time += result.get("processing_time_ms", 0)

                if algo == "segmentation_3d":
                    num_objects = result.get("results", {}).get("num_objects", 0)
                    total_objects += num_objects

        # Display summary
        table = Table(title="Pipeline Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Files Processed", str(len(self.results)))
        table.add_row("Total Objects Detected", str(total_objects))
        table.add_row("Total Processing Time", f"{total_processing_time / 1000:.2f} seconds")
        table.add_row("Average Time per File", f"{total_processing_time / len(self.results) if self.results else 0:.0f} ms")

        console.print("\n")
        console.print(table)

    def _generate_reports(self) -> None:
        """Generate analysis reports"""

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed results
        results_file = self.output_dir / "pipeline_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        console.print(f"  ✓ Detailed results: {results_file}")

        # Generate CSV summary
        summary_file = self.output_dir / "pipeline_summary.csv"
        self._generate_csv_summary(summary_file)

        console.print(f"  ✓ Summary report: {summary_file}")

    def _generate_csv_summary(self, output_path: Path) -> None:
        """Generate CSV summary of results"""

        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "File",
                "Segmentation_Objects",
                "Mean_Intensity",
                "Processing_Time_ms"
            ])

            # Data rows
            for file_result in self.results:
                file_name = Path(file_result["file"]).name

                seg_result = file_result["algorithms"].get("segmentation_3d", {})
                num_objects = seg_result.get("results", {}).get("num_objects", 0)

                intensity_result = file_result["algorithms"].get("intensity_analysis", {})
                mean_intensity = intensity_result.get("results", {}).get("mean_intensity", 0)

                total_time = sum(
                    r.get("processing_time_ms", 0)
                    for r in file_result["algorithms"].values()
                )

                writer.writerow([
                    file_name,
                    num_objects,
                    f"{mean_intensity:.2f}",
                    total_time
                ])


async def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description="Z-Stack Analysis Pipeline")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("./data"),
        help="Input directory containing Z-stack images"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./results/pipeline"),
        help="Output directory for results"
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.input.exists():
        console.print(f"[bold red]Error:[/bold red] Input directory does not exist: {args.input}")
        sys.exit(1)

    # Run pipeline
    pipeline = AnalysisPipeline(args.input, args.output)
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())
