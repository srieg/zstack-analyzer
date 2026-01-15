#!/bin/bash

# Z-Stack Analyzer - One Command Launch
# Usage: ./start.sh [--demo] [--api-only] [--frontend-only]

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${BOLD}🔬 Z-Stack Analyzer${NC} - GPU-Accelerated Microscopy Analysis  ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

DEMO_MODE=false
API_ONLY=false
FRONTEND_ONLY=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --demo)
            DEMO_MODE=true
            shift
            ;;
        --api-only)
            API_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --demo          Start with synthetic demo data"
            echo "  --api-only      Only start the backend API"
            echo "  --frontend-only Only start the frontend"
            echo "  --help, -h      Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to setup Python environment
setup_python() {
    echo -e "${YELLOW}→ Setting up Python environment...${NC}"

    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
    fi

    source venv/bin/activate

    # Check if dependencies are installed
    if ! python -c "import fastapi" 2>/dev/null; then
        echo "  Installing Python dependencies..."
        pip install -q -r requirements.txt
    fi

    echo -e "${GREEN}  ✓ Python environment ready${NC}"
}

# Function to setup frontend
setup_frontend() {
    echo -e "${YELLOW}→ Setting up frontend...${NC}"

    cd "$SCRIPT_DIR/frontend"

    if [ ! -d "node_modules" ]; then
        echo "  Installing npm dependencies..."
        npm install --silent
    fi

    cd "$SCRIPT_DIR"
    echo -e "${GREEN}  ✓ Frontend ready${NC}"
}

# Function to start API
start_api() {
    echo -e "${YELLOW}→ Starting API server...${NC}"

    source venv/bin/activate

    if $DEMO_MODE; then
        export DEMO_MODE=true
    fi

    # Use SQLite by default (no PostgreSQL needed!)
    # Set DATABASE_URL to use PostgreSQL if you want: export DATABASE_URL="postgresql+asyncpg://..."

    cd "$SCRIPT_DIR/api"

    if port_in_use 8000; then
        echo -e "${RED}  ✗ Port 8000 already in use${NC}"
        return 1
    fi

    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    API_PID=$!

    # Wait for API to be ready
    echo "  Waiting for API..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo -e "${GREEN}  ✓ API running at http://localhost:8000${NC}"
            echo -e "${GREEN}  ✓ API docs at http://localhost:8000/docs${NC}"
            return 0
        fi
        sleep 0.5
    done

    echo -e "${RED}  ✗ API failed to start${NC}"
    return 1
}

# Function to start frontend
start_frontend() {
    echo -e "${YELLOW}→ Starting frontend...${NC}"

    cd "$SCRIPT_DIR/frontend"

    if port_in_use 5173; then
        echo -e "${RED}  ✗ Port 5173 already in use${NC}"
        return 1
    fi

    npm run dev &
    FRONTEND_PID=$!

    # Wait for frontend to be ready
    echo "  Waiting for frontend..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 >/dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Frontend running at http://localhost:5173${NC}"
            return 0
        fi
        sleep 0.5
    done

    echo -e "${YELLOW}  ⚠ Frontend may still be starting...${NC}"
    return 0
}

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"

    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Kill any remaining processes on our ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}Done!${NC}"
}

trap cleanup EXIT INT TERM

# Main startup sequence
echo -e "${BOLD}Starting Z-Stack Analyzer...${NC}"
echo ""

if ! $FRONTEND_ONLY; then
    setup_python
fi

if ! $API_ONLY; then
    setup_frontend
fi

echo ""

if $DEMO_MODE; then
    echo -e "${BLUE}📊 Running in DEMO MODE with synthetic data${NC}"
    echo ""
fi

if ! $FRONTEND_ONLY; then
    start_api
fi

if ! $API_ONLY; then
    start_frontend
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                    ${BOLD}🚀 Z-Stack Analyzer Ready!${NC}                 ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Frontend:  ${BLUE}http://localhost:5173${NC}                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  API:       ${BLUE}http://localhost:8000${NC}                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  API Docs:  ${BLUE}http://localhost:8000/docs${NC}                      ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Press ${YELLOW}Ctrl+C${NC} to stop                                       ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Keep the script running
wait
