#!/bin/bash
# Build script for C++ project

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Building project..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring..."
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
echo "Compiling..."
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)

# Run tests
echo "Running tests..."
ctest --output-on-failure

echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "To run the example:"
echo "  ./build/example"
