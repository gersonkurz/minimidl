# TaskManager Swift Project

This project provides Swift bindings for the TaskManager API, generated from MinimIDL interface definitions.

## Project Structure

```
TaskManager/
├── CWrapper/           # C wrapper interface
├── CImplementation/    # C++ implementation stubs
├── TaskManager/     # Swift package
├── ExampleApp/         # Example iOS/macOS app
├── build_c.sh          # Build C libraries
└── build_swift.sh      # Build Swift package
```

## Building

### Step 1: Build C Libraries

```bash
./build_c.sh
```

This builds the C wrapper and C++ implementation.

### Step 2: Build Swift Package

```bash
./build_swift.sh
```

This builds the Swift package that wraps the C libraries.

## Usage

### Swift Package Manager

Add this package to your `Package.swift`:

```swift
dependencies: [
    .package(path: "path/to/TaskManager/TaskManager")
]
```

### Example Code

```swift
import TaskManager

// Create an instance
let instance = MyClass()

// Use the API
// TODO: Add your code here
```

## Available Classes

- `Task` (from TaskManager::ITask)
- `Project` (from TaskManager::IProject)
- `TaskManager` (from TaskManager::ITaskManager)

## Example App

An example iOS/macOS app is provided in the `ExampleApp` directory. To run:

1. Open `ExampleApp/TaskManagerExample.xcodeproj` in Xcode
2. Build and run

## Implementation Notes

The C++ implementation in `CImplementation/` contains stub code. You need to:

1. Implement the actual business logic in the `*_impl.cpp` files
2. Implement the C wrapper factory functions
3. Rebuild using `./build_c.sh`

## Testing

To run Swift tests:

```bash
cd TaskManager
swift test
```

## Generated by MinimIDL

This code was automatically generated. Do not edit the generated files in the Swift package.
