# Z-Stack Analyzer CLI - Installation & Setup

Complete guide to installing and setting up the Z-Stack Analyzer CLI tool.

## System Requirements

- Python 3.11 or higher
- 8GB RAM minimum (16GB+ recommended for batch processing)
- GPU (optional, but recommended for 10-15x speedup)
  - NVIDIA GPU with CUDA support, or
  - Apple Silicon with Metal support

## Installation

### Step 1: Navigate to Project Directory

```bash
cd /Users/samriegel/zstack-analyzer
```

### Step 2: Install in Development Mode

```bash
# Install with all dependencies
pip install -e .

# Or install with specific dependency groups
pip install -e ".[dev]"  # Includes testing tools
pip install -e ".[docs]" # Includes documentation tools
```

### Step 3: Verify Installation

```bash
# Check that the CLI is installed
zstack --version

# Should output: Z-Stack Analyzer version 0.1.0

# Check available commands
zstack --help
```

## Dependencies

The CLI installation includes:

### Core Dependencies
- `typer>=0.9.0` - CLI framework with beautiful help
- `rich>=13.0.0` - Rich terminal output and progress bars
- `pyyaml>=6.0` - YAML configuration support
- `psutil>=5.9.0` - System and process utilities
- `requests>=2.31.0` - HTTP library for server status checks

### Scientific Computing
- `numpy>=1.24.0` - Numerical computing
- `scikit-image>=0.22.0` - Image processing
- `scipy>=1.11.0` - Scientific computing

### Web Server
- `fastapi>=0.104.0` - Modern web framework
- `uvicorn[standard]>=0.24.0` - ASGI server

## Configuration

### User-Level Configuration

Create a config file at `~/.zstack-analyzer.yaml`:

```bash
# Copy example config
cp examples/automation.yaml ~/.zstack-analyzer.yaml

# Edit with your preferences
nano ~/.zstack-analyzer.yaml
```

### Project-Level Configuration

For project-specific settings, create `.zstack-analyzer.yaml` in your project directory:

```bash
cd /path/to/your/project
cp /Users/samriegel/zstack-analyzer/examples/automation.yaml .zstack-analyzer.yaml
```

### Configuration Priority

Settings are loaded in this order (later overrides earlier):
1. Default values
2. User-level config (`~/.zstack-analyzer.yaml`)
3. Project-level config (`./.zstack-analyzer.yaml`)
4. Command-line arguments (highest priority)

## GPU Setup

### NVIDIA GPU (CUDA)

```bash
# Install CUDA toolkit (if not already installed)
# Visit: https://developer.nvidia.com/cuda-downloads

# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Apple Silicon (Metal)

```bash
# Metal support is built into PyTorch for Apple Silicon
# Verify Metal is available
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

Configure GPU in your YAML:

```yaml
gpu:
  enabled: true
  device: cuda:0  # or 'metal' for Apple Silicon
  memory_limit_mb: 8192
  fallback_to_cpu: true
```

## Testing the Installation

### Quick Test

```bash
# Run quick benchmark
zstack benchmark quick
```

### Full Test Suite

```bash
# Generate synthetic test data
python -c "
import numpy as np
from pathlib import Path
data = np.random.randint(0, 65535, (50, 512, 512), dtype=np.uint16)
from skimage import io
Path('./test_data').mkdir(exist_ok=True)
io.imsave('./test_data/test.tif', data)
"

# Run analysis
zstack analyze single ./test_data/test.tif --output ./test_results/

# Check results
cat ./test_results/test_results.json
```

## Command Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(_ZSTACK_COMPLETE=bash_source zstack)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_ZSTACK_COMPLETE=zsh_source zstack)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
_ZSTACK_COMPLETE=fish_source zstack | source
```

## Directory Structure

After installation, your CLI structure looks like:

```
zstack-analyzer/
├── cli/                          # CLI package
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── config.py                # Configuration management
│   ├── README.md                # Full documentation
│   ├── QUICKSTART.md            # Quick start guide
│   └── commands/                # Command modules
│       ├── __init__.py
│       ├── analyze.py           # Analysis commands
│       ├── info.py              # Info commands
│       ├── convert.py           # Conversion commands
│       ├── benchmark.py         # Benchmark commands
│       └── serve.py             # Server commands
├── examples/                     # Example scripts
│   ├── batch_analysis.sh        # Bash example
│   ├── pipeline.py              # Python example
│   └── automation.yaml          # Config example
├── core/                         # Core analysis engine
├── api/                          # Web API
└── pyproject.toml               # Package configuration
```

## Common Issues

### Issue: Command not found

```bash
# Solution 1: Reinstall
pip uninstall zstack-analyzer
pip install -e .

# Solution 2: Use Python module syntax
python -m cli analyze single image.tif
```

### Issue: Import errors

```bash
# Install missing dependencies
pip install -r requirements.txt

# Or reinstall with all dependencies
pip install -e ".[dev,docs]"
```

### Issue: GPU not detected

```bash
# Check GPU drivers
nvidia-smi  # For NVIDIA
system_profiler SPDisplaysDataType  # For macOS

# Force CPU mode
zstack analyze single image.tif --gpu none
```

### Issue: Slow performance

```bash
# Run benchmark to diagnose
zstack benchmark run --memory

# Check if parallel processing is enabled
zstack analyze batch ./data/ --parallel 8  # Increase workers
```

## Updating

```bash
# Pull latest changes
cd /Users/samriegel/zstack-analyzer
git pull

# Reinstall
pip install -e . --upgrade
```

## Uninstallation

```bash
pip uninstall zstack-analyzer
rm -rf ~/.zstack-analyzer.yaml  # Remove user config (optional)
```

## Next Steps

1. Read the [Quick Start Guide](cli/QUICKSTART.md)
2. Review [Example Scripts](examples/)
3. Read the [Full CLI Documentation](cli/README.md)
4. Configure your workflows in `~/.zstack-analyzer.yaml`

## Support

- Documentation: `cli/README.md`
- Examples: `examples/` directory
- Issues: GitHub Issues
- License: Apache-2.0 (see LICENSE file)
