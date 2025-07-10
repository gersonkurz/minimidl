#!/bin/bash
# Build Swift package

set -e

echo "Building Swift package for TaskManager..."

# Ensure C libraries are built first
if [ ! -d "build_c" ]; then
    echo "C libraries not built. Running build_c.sh first..."
    ./build_c.sh
fi

# Set library paths for linking
export LIBRARY_PATH="$PWD/build_c:$LIBRARY_PATH"
export LD_LIBRARY_PATH="$PWD/build_c:$LD_LIBRARY_PATH"
export DYLD_LIBRARY_PATH="$PWD/build_c:$DYLD_LIBRARY_PATH"

# Build Swift package
cd TaskManager
swift build -c release

echo "Swift package built successfully!"
echo "To run tests: cd TaskManager && swift test"
