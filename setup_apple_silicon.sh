#!/bin/bash

# Z-Stack Analyzer - Apple Silicon Optimized Setup
# Specifically optimized for Apple Silicon Macs (M1/M2/M3/M4)

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   ${BOLD}🍎 Z-Stack Analyzer - Apple Silicon Setup${NC}                ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verify Apple Silicon
echo -e "${BOLD}Verifying Apple Silicon platform...${NC}"
echo ""

ARCH=$(uname -m)
OS=$(uname -s)

if [[ "$ARCH" != "arm64" ]]; then
    echo -e "${RED}  ✗ Not running on Apple Silicon (detected: $ARCH)${NC}"
    echo "    This script is specifically for Apple Silicon Macs."
    echo "    Use ./setup.sh for Intel Macs or other platforms."
    exit 1
fi

if [[ "$OS" != "Darwin" ]]; then
    echo -e "${RED}  ✗ Not running on macOS (detected: $OS)${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Apple Silicon Mac detected${NC}"

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)

echo -e "${GREEN}  ✓ macOS ${MACOS_VERSION}${NC}"

if [[ $MACOS_MAJOR -lt 12 ]]; then
    echo -e "${YELLOW}  ⚠ macOS 12+ recommended for best Metal performance${NC}"
fi

# Check Xcode Command Line Tools
echo ""
echo -e "${BOLD}Checking development tools...${NC}"
echo ""

if ! xcode-select -p &> /dev/null; then
    echo -e "${YELLOW}  ! Xcode Command Line Tools not found${NC}"
    echo "    Installing Xcode Command Line Tools..."
    xcode-select --install
    echo "    Please complete the installation and run this script again."
    exit 1
fi

echo -e "${GREEN}  ✓ Xcode Command Line Tools installed${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_ARCH=$(python3 -c "import platform; print(platform.machine())")

    if [[ "$PYTHON_ARCH" == "arm64" ]]; then
        echo -e "${GREEN}  ✓ Python ${PYTHON_VERSION} (ARM64 native)${NC}"
    else
        echo -e "${YELLOW}  ⚠ Python ${PYTHON_VERSION} (running under Rosetta 2)${NC}"
        echo "    Install ARM64 native Python from https://www.python.org/downloads/"
        echo "    for best performance."
    fi
else
    echo -e "${RED}  ✗ Python 3 not found${NC}"
    echo "    Please install Python 3.11 or later from https://www.python.org/"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NODE_ARCH=$(node -p "process.arch")

    if [[ "$NODE_ARCH" == "arm64" ]]; then
        echo -e "${GREEN}  ✓ Node.js ${NODE_VERSION} (ARM64 native)${NC}"
    else
        echo -e "${YELLOW}  ⚠ Node.js ${NODE_VERSION} (x64 - consider ARM64 version)${NC}"
    fi
else
    echo -e "${RED}  ✗ Node.js not found${NC}"
    echo "    Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Metal support
echo ""
echo -e "${BOLD}Checking GPU support...${NC}"
echo ""

if system_profiler SPDisplaysDataType 2>/dev/null | grep -q "Metal"; then
    GPU_INFO=$(system_profiler SPDisplaysDataType 2>/dev/null | grep "Chipset Model" | head -1 | sed 's/.*: //')
    echo -e "${GREEN}  ✓ Metal GPU: ${GPU_INFO}${NC}"
    echo "    Full Metal acceleration available"
else
    echo -e "${YELLOW}  ⚠ Metal GPU detection failed${NC}"
fi

# Setup Python environment
echo ""
echo -e "${BOLD}Setting up Python environment...${NC}"
echo ""

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "  Upgrading pip..."
pip install --upgrade pip -q

echo "  Installing core dependencies..."
pip install -r requirements.txt -q

# Install tinygrad with Metal support
echo "  Installing tinygrad (Metal GPU acceleration)..."
if [ -d "tinygrad" ]; then
    cd tinygrad
    pip install -e . -q
    cd "$SCRIPT_DIR"
else
    pip install tinygrad -q
fi

# Install microscopy format support
echo "  Installing microscopy format libraries..."
pip install tifffile aicspylibczi nd2 readlif zarr dask -q

echo -e "${GREEN}  ✓ Python environment ready${NC}"

# Setup frontend
echo ""
echo -e "${BOLD}Setting up frontend...${NC}"
echo ""

cd "$SCRIPT_DIR/frontend"

echo "  Installing npm dependencies..."
npm install --silent

echo -e "${GREEN}  ✓ Frontend ready${NC}"

# Create directories
echo ""
echo -e "${BOLD}Setting up directories...${NC}"
echo ""

cd "$SCRIPT_DIR"
mkdir -p data uploads thumbnails

echo -e "${GREEN}  ✓ Directories created${NC}"

# Verify Metal GPU initialization
echo ""
echo -e "${BOLD}Verifying Metal GPU initialization...${NC}"
echo ""

python3 -c "
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'tinygrad')

try:
    from core.gpu.device_manager import DeviceManager
    from tinygrad.tensor import Tensor

    dm = DeviceManager()

    if dm.is_metal:
        print('${GREEN}  ✓ Metal GPU initialized successfully${NC}')
        print(f'    Device: {dm.device_info.get(\"name\", \"Unknown\")}')

        # Test tensor operation
        test = Tensor([1.0, 2.0, 3.0], device='METAL')
        result = test.realize()
        print('${GREEN}  ✓ GPU tensor operations working${NC}')
    else:
        print('${YELLOW}  ⚠ Metal GPU not detected, using CPU${NC}')
        print('    Performance will be degraded.')

except Exception as e:
    print('${RED}  ✗ GPU initialization failed${NC}')
    print(f'    Error: {e}')
    sys.exit(1)
" || {
    echo -e "${RED}GPU verification failed. Check APPLE_SILICON_GUIDE.md for troubleshooting.${NC}"
    exit 1
}

# Run comprehensive verification
echo ""
echo -e "${BOLD}Running comprehensive verification...${NC}"
echo ""

python3 verify_apple_silicon.py || {
    echo ""
    echo -e "${YELLOW}Some verification checks failed.${NC}"
    echo -e "${YELLOW}Review the output above and consult APPLE_SILICON_GUIDE.md${NC}"
}

# Done!
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}              ${BOLD}✨ Apple Silicon Setup Complete!${NC}                  ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Your Z-Stack Analyzer is optimized for:                    ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    🍎 Native ARM64 execution                                ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    ⚡ Metal GPU acceleration                                 ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    🚀 Apple Accelerate framework                            ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  To start the application:                                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    ${BLUE}./start.sh${NC}                                               ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  For help and optimization tips:                            ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    ${BLUE}cat APPLE_SILICON_GUIDE.md${NC}                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
