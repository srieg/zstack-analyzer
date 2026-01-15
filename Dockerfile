# Multi-stage build for Z-Stack Analyzer
FROM nvidia/cuda:12.2-devel-ubuntu22.04 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt pyproject.toml ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Install tinygrad from source (for latest GPU support)
RUN pip3 install git+https://github.com/tinygrad/tinygrad.git

# Copy Rust decoder source
COPY decoders/ ./decoders/
RUN cd decoders && cargo build --release

# Copy Python source code
COPY core/ ./core/
COPY api/ ./api/

# Install the package
RUN pip3 install -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]