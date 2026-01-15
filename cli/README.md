# Z-Stack Analyzer CLI

A powerful command-line interface for batch processing and automation of confocal microscopy Z-stack analysis.

## Features

- 🚀 **Fast Batch Processing** - Process hundreds of images in parallel
- 🎨 **Beautiful Output** - Rich terminal UI with progress bars and tables
- 🔧 **Flexible Configuration** - YAML-based config files for reproducible workflows
- ⚡ **GPU Acceleration** - Automatic GPU detection and utilization
- 📊 **Multiple Formats** - Support for TIFF, OME-TIFF, CZI, HDF5, and Zarr
- 🧪 **Performance Benchmarking** - Built-in tools for profiling and optimization
- 🌐 **Web Server Management** - Integrated API server controls

## Installation

```bash
# Install from project directory
cd /Users/samriegel/zstack-analyzer
pip install -e .

# Or install dependencies manually
pip install typer rich pyyaml psutil requests
```

## Quick Start

```bash
# Analyze a single file
zstack analyze single image.tif --algorithm segmentation_3d

# Batch process a directory
zstack analyze batch ./data/ --output ./results/ --parallel 8

# Show file information
zstack info image.tif

# Convert formats
zstack convert input.tif output.ome.tif --compression lzw

# Run benchmarks
zstack benchmark run --iterations 20

# Start web server
zstack serve start --port 8000
```

## Commands

### Analyze

Process Z-stack images with various algorithms.

```bash
# Single file analysis
zstack analyze single image.tif \
    --algorithm segmentation_3d \
    --threshold 0.5 \
    --min-object-size 100 \
    --output ./results/ \
    --format json

# Batch processing
zstack analyze batch ./data/ \
    --output ./results/ \
    --algorithm colocalization \
    --parallel 8 \
    --pattern "*.tif"

# List available algorithms
zstack analyze list-algorithms
```

**Available Algorithms:**
- `segmentation_3d` - 3D cell segmentation
- `colocalization` - Multi-channel colocalization
- `intensity_analysis` - Intensity statistics
- `deconvolution` - Richardson-Lucy deconvolution

### Info

Display file metadata and quick preview statistics.

```bash
# Show file information
zstack info image.tif

# Verbose output
zstack info image.tif --verbose

# Batch info
zstack info batch ./data/ --pattern "*.tif"
```

### Convert

Convert between image formats with compression options.

```bash
# Basic conversion
zstack convert input.tif output.ome.tif

# With compression
zstack convert input.czi output.tif \
    --compression lzw \
    --bit-depth 16

# Batch conversion
zstack convert batch ./input/ ./output/ \
    --format ome.tif \
    --pattern "*.czi" \
    --compression zip
```

**Supported Formats:**
- Input: TIFF, OME-TIFF, CZI, ND2, LSM
- Output: TIFF, OME-TIFF, HDF5, Zarr

### Benchmark

Run performance benchmarks and profiling.

```bash
# Full benchmark suite
zstack benchmark run --iterations 20

# Quick benchmark
zstack benchmark quick

# Custom benchmark with specific file
zstack benchmark run \
    --file test.tif \
    --algorithms segmentation_3d,colocalization \
    --output benchmark_results.md
```

### Serve

Start and manage the web server.

```bash
# Start server
zstack serve start --port 8000 --workers 4

# Development mode (with auto-reload)
zstack serve dev

# Production mode (optimized settings)
zstack serve prod

# Check server status
zstack serve status
```

## Configuration

Create a configuration file at `~/.zstack-analyzer.yaml` or `./.zstack-analyzer.yaml`:

```yaml
# Analysis settings
analysis:
  default_algorithm: segmentation_3d
  threshold: 0.5
  min_object_size: 100
  output_format: json
  parallel_workers: 8

# GPU settings
gpu:
  enabled: true
  device: cuda:0
  memory_limit_mb: 8192
  fallback_to_cpu: true

# Output settings
output:
  default_directory: ./results
  compression: lzw
  quality: 95
  save_metadata: true
  verbose: false

# Server settings
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  log_level: info
```

## Examples

### Example 1: High-Throughput Screening

```bash
# Process 100 images in parallel with segmentation
zstack analyze batch ./screening_data/ \
    --output ./screening_results/ \
    --algorithm segmentation_3d \
    --parallel 16 \
    --format csv \
    --threshold 0.6
```

### Example 2: Multi-Algorithm Pipeline

See `examples/pipeline.py` for a complete example of running multiple algorithms in sequence.

```bash
python examples/pipeline.py \
    --input ./data/ \
    --output ./results/pipeline/
```

### Example 3: Automated Workflow

Use the example configuration and bash script:

```bash
# Copy and customize the automation config
cp examples/automation.yaml ~/.zstack-analyzer.yaml

# Run batch analysis
./examples/batch_analysis.sh ./data/ ./results/ segmentation_3d
```

## Performance Tips

1. **Parallel Processing**: Use `--parallel` to match your CPU core count
2. **GPU Acceleration**: Enable GPU in config for 10-15x speedup
3. **Compression**: Use LZW or ZIP compression for TIFF files to save disk space
4. **Batch Size**: Process 50-100 files at a time for optimal memory usage
5. **Output Format**: Use CSV for spreadsheet analysis, JSON for programmatic access

## Output Formats

### JSON Output
```json
{
  "algorithm": "segmentation_3d",
  "version": "1.0.0",
  "processing_time_ms": 1245,
  "results": {
    "num_objects": 47,
    "mean_volume": 1234.5,
    "total_volume": 58021.5
  }
}
```

### CSV Output
```csv
file_path,algorithm,num_objects,mean_volume,processing_time_ms
image1.tif,segmentation_3d,47,1234.5,1245
image2.tif,segmentation_3d,52,1189.2,1198
```

## Troubleshooting

### GPU Not Detected
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU mode
zstack analyze single image.tif --gpu none
```

### Out of Memory
```bash
# Reduce parallel workers
zstack analyze batch ./data/ --parallel 2

# Or process files individually
for f in data/*.tif; do
    zstack analyze single "$f" --output ./results/
done
```

### Slow Performance
```bash
# Run benchmark to identify bottlenecks
zstack benchmark run --file test.tif --memory

# Check if GPU is being utilized
# Monitor with nvidia-smi (NVIDIA) or Activity Monitor (macOS)
```

## Integration with Other Tools

### Python Scripts
```python
from cli.config import get_config

config = get_config()
threshold = config.get_value('analysis', 'threshold')
```

### Shell Scripts
```bash
#!/bin/bash
# Process all subdirectories
for dir in data/*/; do
    zstack analyze batch "$dir" \
        --output "results/$(basename $dir)/"
done
```

## Contributing

See `CONTRIBUTING.md` in the project root for development guidelines.

## License

Apache-2.0 License - See `LICENSE` file for details.
