#!/bin/bash
# Build C wrapper and implementation

set -e

echo "Building C wrapper and implementation for TaskManager..."

# Create build directory
mkdir -p build_c
cd build_c

# Configure
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)

echo "C libraries built successfully!"
echo "Libraries are in: build_c/"
