# Installation

MinimIDL requires Python 3.13 or later.

## Using pip

```bash
pip install minimidl
```

## Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package manager:

```bash
uv pip install minimidl
```

## From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/minimidl.git
cd minimidl
pip install -e ".[dev]"
```

## Verify Installation

```bash
minimidl --version
```

You should see:
```
MinimIDL version 0.1.0
```

## System Requirements

### For Code Generation
- Python 3.13+
- No additional dependencies needed

### For Using Generated C++ Code
- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.16+
- Standard C++ library

### For Using Generated Swift Code
- Swift 5.7+
- Xcode 14+ (macOS)
- Swift Package Manager

## Platform Support

MinimIDL is tested on:
- macOS 12+ (primary platform)
- Ubuntu 20.04+
- Windows 10/11 (with Visual Studio 2019+)

## Development Setup

For contributing to MinimIDL:

```bash
# Clone repository
git clone https://github.com/yourusername/minimidl.git
cd minimidl

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
mypy .

# Format code
black .
isort .
```

## Next Steps

Now that you have MinimIDL installed, check out the [Quick Start Guide](quickstart.md) to create your first interface definition.