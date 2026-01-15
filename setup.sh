#!/bin/bash

# Z-Stack Analyzer - First Time Setup
# This script sets up everything needed to run Z-Stack Analyzer

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}         ${BOLD}🔬 Z-Stack Analyzer Setup${NC}                             ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check prerequisites
echo -e "${BOLD}Checking prerequisites...${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}  ✓ Python ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}  ✗ Python 3 not found${NC}"
    echo "    Please install Python 3.11 or later"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}  ✓ Node.js ${NODE_VERSION}${NC}"
else
    echo -e "${RED}  ✗ Node.js not found${NC}"
    echo "    Please install Node.js 18 or later"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}  ✓ npm ${NPM_VERSION}${NC}"
else
    echo -e "${RED}  ✗ npm not found${NC}"
    exit 1
fi

# Check for GPU (optional)
echo ""
echo -e "${BOLD}Checking GPU support...${NC}"
echo ""

GPU_AVAILABLE=false

# Check for NVIDIA GPU (Linux/WSL)
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    if [ ! -z "$GPU_INFO" ]; then
        echo -e "${GREEN}  ✓ NVIDIA GPU: ${GPU_INFO}${NC}"
        GPU_AVAILABLE=true
    fi
fi

# Check for Metal (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if system_profiler SPDisplaysDataType 2>/dev/null | grep -q "Metal"; then
        GPU_INFO=$(system_profiler SPDisplaysDataType 2>/dev/null | grep "Chipset Model" | head -1 | sed 's/.*: //')
        echo -e "${GREEN}  ✓ Apple GPU (Metal): ${GPU_INFO}${NC}"
        GPU_AVAILABLE=true
    fi
fi

if ! $GPU_AVAILABLE; then
    echo -e "${YELLOW}  ⚠ No GPU detected - will use CPU (slower)${NC}"
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

echo "  Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Install tinygrad
echo "  Installing tinygrad (GPU acceleration)..."
if [ -d "tinygrad" ]; then
    cd tinygrad
    pip install -e . -q
    cd "$SCRIPT_DIR"
else
    pip install tinygrad -q
fi

echo -e "${GREEN}  ✓ Python environment ready${NC}"

# Setup frontend
echo ""
echo -e "${BOLD}Setting up frontend...${NC}"
echo ""

cd "$SCRIPT_DIR/frontend"

echo "  Installing npm dependencies..."
npm install --silent

echo -e "${GREEN}  ✓ Frontend ready${NC}"

# Create data directory
echo ""
echo -e "${BOLD}Setting up directories...${NC}"
echo ""

cd "$SCRIPT_DIR"
mkdir -p data uploads

echo -e "${GREEN}  ✓ Directories created${NC}"

# Done!
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}              ${BOLD}✨ Setup Complete!${NC}                                ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  To start Z-Stack Analyzer, run:                            ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    ${BLUE}./start.sh${NC}                                               ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Or with demo data:                                         ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    ${BLUE}./start.sh --demo${NC}                                        ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                              ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
