# Contributing to Z-Stack Analyzer

Thank you for your interest in contributing to the Z-Stack Analyzer project! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.11+
- Rust 1.70+
- Node.js 18+
- NVIDIA GPU with CUDA support (recommended)
- Docker and Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/zstack-analyzer.git
   cd zstack-analyzer
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Install tinygrad from source**
   ```bash
   git clone https://github.com/tinygrad/tinygrad.git
   cd tinygrad
   pip install -e .
   cd ..
   ```

4. **Build Rust decoders**
   ```bash
   cd decoders
   cargo build --release
   cd ..
   ```

5. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

6. **Set up database**
   ```bash
   # Using Docker
   docker-compose up postgres -d
   
   # Or install PostgreSQL locally and create database
   createdb zstack_analyzer
   ```

7. **Run the application**
   ```bash
   # Terminal 1: API server
   cd api
   uvicorn main:app --reload
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## Code Style and Standards

### Python

- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`
- Use mypy for type checking: `mypy .`
- Follow PEP 8 guidelines
- Add type hints to all functions
- Write docstrings for public functions and classes

### Rust

- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting
- Follow Rust naming conventions
- Add documentation comments for public APIs

### TypeScript/React

- Use ESLint and Prettier for formatting
- Follow React best practices
- Use TypeScript strict mode
- Prefer functional components with hooks

## Testing

### Python Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=api

# Run specific test file
pytest tests/test_image_loader.py
```

### Rust Tests

```bash
cd decoders
cargo test
```

### Frontend Tests

```bash
cd frontend
npm test
```

## GPU Development

### CUDA Setup

Ensure you have CUDA 12.0+ installed and configured:

```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# Test tinygrad GPU support
python -c "from tinygrad.tensor import Tensor; print(Tensor([1,2,3]).gpu())"
```

### Performance Testing

When working on GPU-accelerated features:

1. Profile memory usage with `nvidia-smi`
2. Benchmark against CPU implementations
3. Test with different image sizes
4. Verify memory cleanup after processing

## Submitting Changes

### Pull Request Process

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run the full test suite**
   ```bash
   # Python tests
   pytest
   
   # Rust tests
   cd decoders && cargo test
   
   # Frontend tests
   cd frontend && npm test
   
   # Type checking
   mypy .
   
   # Linting
   black . && isort .
   ```

6. **Commit your changes** with descriptive messages
   ```bash
   git commit -m "Add 3D segmentation algorithm using tinygrad"
   ```

7. **Push to your fork** and create a pull request

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when applicable

## Issue Reporting

### Bug Reports

Include the following information:

- Operating system and version
- Python version
- GPU model and CUDA version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces
- Sample data (if applicable)

### Feature Requests

- Describe the problem you're trying to solve
- Explain why this feature would be useful
- Provide examples of how it would be used
- Consider implementation complexity

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Include parameter types and return types
- Provide usage examples for complex functions
- Document any assumptions or limitations

### User Documentation

- Update README.md for new features
- Add examples to the examples/ directory
- Update API documentation
- Include performance benchmarks

## Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Provide constructive feedback
- Follow the code of conduct

## Getting Help

- Join our Discord server: [link]
- Check existing issues and discussions
- Ask questions in pull request comments
- Reach out to maintainers directly

## License

By contributing to Z-Stack Analyzer, you agree that your contributions will be licensed under the Apache 2.0 License.