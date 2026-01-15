# Z-Stack Analyzer CLI - Quick Reference Card

## Installation
```bash
cd /Users/samriegel/zstack-analyzer && pip install -e .
```

## Essential Commands

### Analysis
```bash
# Single file
zstack analyze single image.tif

# Batch processing
zstack analyze batch ./data/ -o ./results/ -p 8

# List algorithms
zstack analyze list-algorithms
```

### Information
```bash
# File metadata
zstack info image.tif

# Batch info
zstack info batch ./data/
```

### Conversion
```bash
# Single conversion
zstack convert input.tif output.ome.tif -c lzw

# Batch conversion
zstack convert batch ./input/ ./output/ -f ome.tif
```

### Benchmarking
```bash
# Quick test
zstack benchmark quick

# Full benchmark
zstack benchmark run -i 20 -o results.md
```

### Server
```bash
# Start server
zstack serve start

# Development mode
zstack serve dev

# Check status
zstack serve status
```

## Common Options

| Option | Short | Description |
|--------|-------|-------------|
| `--algorithm` | `-a` | Analysis algorithm |
| `--output` | `-o` | Output directory |
| `--format` | `-f` | Output format (json/csv/hdf5) |
| `--parallel` | `-p` | Parallel workers (1-32) |
| `--gpu` | `-g` | GPU device selection |
| `--compression` | `-c` | Compression (lzw/zip/jpeg) |
| `--verbose` | `-v` | Verbose output |
| `--help` | `-h` | Show help |

## Configuration File

Location: `~/.zstack-analyzer.yaml`

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

## Algorithms

- `segmentation_3d` - 3D cell segmentation
- `colocalization` - Multi-channel colocalization
- `intensity_analysis` - Intensity statistics
- `deconvolution` - Richardson-Lucy deconvolution

## Output Formats

- `json` - Structured JSON (default)
- `csv` - Spreadsheet-compatible
- `hdf5` - Large dataset storage

## Compression

- `none` - No compression
- `lzw` - Lossless (recommended)
- `zip` - Lossless
- `jpeg` - Lossy (for previews)

## Examples

```bash
# High-throughput screening
zstack analyze batch ./screening/ -o ./results/ -a segmentation_3d -p 16 -f csv

# Format conversion pipeline
zstack convert batch ./raw/ ./converted/ -f ome.tif -c lzw

# Performance comparison
zstack benchmark run --gpu --memory -o benchmark.md

# Web API server
zstack serve start --port 8000 --workers 4
```

## File Patterns

```bash
# Process only .tif files
zstack analyze batch ./data/ --pattern "*.tif"

# Process .czi files
zstack info batch ./data/ --pattern "*.czi"
```

## Troubleshooting

```bash
# Check version
zstack --version

# Get help
zstack --help
zstack analyze --help

# Force CPU mode
zstack analyze single image.tif --gpu none

# Verbose output
zstack analyze single image.tif -v
```

## Documentation

- Full docs: `cli/README.md`
- Quick start: `cli/QUICKSTART.md`
- Installation: `CLI_INSTALLATION.md`
- Examples: `examples/`
