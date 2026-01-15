# Z-Stack Analyzer CLI - Quick Start Guide

Get started with the Z-Stack Analyzer CLI in 5 minutes.

## Installation

```bash
cd /Users/samriegel/zstack-analyzer
pip install -e .
```

## Basic Usage

### 1. Analyze Your First Image

```bash
zstack analyze single image.tif
```

This will:
- Load the image
- Run 3D segmentation (default algorithm)
- Display results in a beautiful table
- Show processing time and confidence scores

### 2. Get File Information

```bash
zstack info image.tif
```

See:
- File dimensions (width × height × depth)
- Number of channels
- Pixel sizes and physical dimensions
- Acquisition metadata

### 3. Batch Process Multiple Files

```bash
zstack analyze batch ./data/ --output ./results/
```

Process all TIFF files in a directory with:
- Automatic parallel processing (4 workers by default)
- Progress bar showing real-time status
- Individual and combined results

### 4. Start the Web Server

```bash
zstack serve start
```

Access the API at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Common Commands

```bash
# List available algorithms
zstack analyze list-algorithms

# Convert file format
zstack convert input.tif output.ome.tif --compression lzw

# Run quick benchmark
zstack benchmark quick

# Check server status
zstack serve status

# Get help
zstack --help
zstack analyze --help
```

## Configuration

Create `~/.zstack-analyzer.yaml`:

```yaml
analysis:
  default_algorithm: segmentation_3d
  threshold: 0.5
  parallel_workers: 8

gpu:
  enabled: true
  device: cuda:0

output:
  default_directory: ./results
  compression: lzw
```

## Next Steps

1. **Customize algorithms**: Use `--threshold` and other parameters
2. **Batch processing**: Process hundreds of images with `--parallel`
3. **Automation**: See `examples/` directory for pipeline examples
4. **Performance**: Run benchmarks to optimize settings

## Examples

### High-Throughput Analysis
```bash
zstack analyze batch ./screening/ \
    --output ./results/ \
    --algorithm segmentation_3d \
    --parallel 16 \
    --format csv
```

### Multi-Channel Colocalization
```bash
zstack analyze single image.tif \
    --algorithm colocalization \
    --output ./results/
```

### Format Conversion
```bash
zstack convert batch ./input/ ./output/ \
    --format ome.tif \
    --pattern "*.czi"
```

## Getting Help

- Full documentation: `cli/README.md`
- Example scripts: `examples/`
- Issue tracker: GitHub Issues

## Tips

1. Use `--help` on any command for detailed options
2. Enable verbose output with `--verbose` for debugging
3. Save benchmark results to track performance over time
4. Use configuration files to standardize team workflows
