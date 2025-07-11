"""Swift project generation workflow."""

from pathlib import Path
from typing import Any

from loguru import logger

from minimidl.ast.nodes import IDLFile
from minimidl.generators.c_wrapper import CWrapperGenerator
from minimidl.generators.swift import SwiftGenerator


class SwiftWorkflow:
    """Workflow for generating complete Swift projects with C wrapper."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize Swift workflow.

        Args:
            config: Optional configuration options
        """
        self.config = config or {}
        self.swift_generator = SwiftGenerator()
        self.c_wrapper_generator = CWrapperGenerator()

    def generate_project(
        self, idl_file: IDLFile, output_dir: Path, project_name: str | None = None
    ) -> list[Path]:
        """Generate a complete Swift project with C wrapper.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Output directory for the project
            project_name: Optional project name (defaults to namespace name)

        Returns:
            List of generated file paths
        """
        logger.info(f"Generating Swift project in {output_dir}")
        generated_files = []

        # Get project name from first namespace if not provided
        if not project_name and idl_file.namespaces:
            project_name = idl_file.namespaces[0].name

        project_name = project_name or "Generated"

        # Create project structure
        project_dir = output_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create directories for C wrapper and implementation
        c_wrapper_dir = project_dir / "CWrapper"
        c_wrapper_dir.mkdir(exist_ok=True)

        # Only create CImplementation dir if we're generating C++ stubs
        if self.config.get("include_cpp_stubs", False):
            c_impl_dir = project_dir / "CImplementation"
            c_impl_dir.mkdir(exist_ok=True)

        # Generate C wrapper first
        logger.info("Generating C wrapper...")
        c_files = self.c_wrapper_generator.generate(idl_file, c_wrapper_dir)
        generated_files.extend(c_files)

        # Generate C++ implementation stubs only if explicitly requested
        # Note: Swift bindings only need the C wrapper, not C++ implementation
        if self.config.get("include_cpp_stubs", False):
            cpp_impl_files = self._generate_cpp_implementation(idl_file, c_impl_dir)
            generated_files.extend(cpp_impl_files)

        # Generate Swift package
        logger.info("Generating Swift package...")
        swift_files = self.swift_generator.generate(idl_file, project_dir)
        generated_files.extend(swift_files)

        # Generate build scripts
        build_c_content = self._generate_c_build_script(project_name)
        build_c_path = self._write_file(project_dir / "build_c.sh", build_c_content)
        build_c_path.chmod(0o755)
        generated_files.append(build_c_path)

        build_swift_content = self._generate_swift_build_script(project_name)
        build_swift_path = self._write_file(project_dir / "build_swift.sh", build_swift_content)
        build_swift_path.chmod(0o755)
        generated_files.append(build_swift_path)

        # Generate comprehensive README
        readme_content = self._generate_project_readme(project_name, idl_file)
        readme_path = self._write_file(project_dir / "README.md", readme_content)
        generated_files.append(readme_path)

        # Generate example app
        example_files = self._generate_example_app(project_name, idl_file, project_dir)
        generated_files.extend(example_files)

        logger.success(
            f"Generated Swift project with {len(generated_files)} files in {project_dir}"
        )
        return generated_files

    def _generate_cpp_implementation(
        self, idl_file: IDLFile, output_dir: Path
    ) -> list[Path]:
        """Generate C++ implementation stubs."""
        generated = []

        for namespace in idl_file.namespaces:
            # Generate implementation header
            impl_h_content = self._generate_impl_header(namespace)
            impl_h_path = self._write_file(
                output_dir / f"{namespace.name}_impl.hpp", impl_h_content
            )
            generated.append(impl_h_path)

            # Generate implementation source
            impl_cpp_content = self._generate_impl_source(namespace)
            impl_cpp_path = self._write_file(
                output_dir / f"{namespace.name}_impl.cpp", impl_cpp_content
            )
            generated.append(impl_cpp_path)

        # Generate CMakeLists.txt for C implementation
        cmake_content = self._generate_impl_cmake(idl_file)
        cmake_path = self._write_file(output_dir / "CMakeLists.txt", cmake_content)
        generated.append(cmake_path)

        return generated

    def _generate_impl_header(self, namespace: Any) -> str:
        """Generate implementation header stub."""
        includes = f'#include "{namespace.name}_wrapper.h"\n#include <string>\n#include <vector>\n#include <memory>'

        impl_classes = []
        for interface in namespace.interfaces:
            class_name = interface.name[1:] if interface.name.startswith("I") else interface.name
            impl_classes.append(
                f"""
// Implementation of {interface.name}
class {class_name}Impl {{
public:
    {class_name}Impl();
    ~{class_name}Impl();
    
    // TODO: Add your implementation here
    // This is a stub implementation for demonstration
}};"""
            )

        impl_section = "\n".join(impl_classes)

        return f"""#pragma once

{includes}

namespace {namespace.name} {{
{impl_section}

}} // namespace {namespace.name}
"""

    def _generate_impl_source(self, namespace: Any) -> str:
        """Generate implementation source stub."""
        return f"""#include "{namespace.name}_impl.hpp"
#include <iostream>

namespace {namespace.name} {{

// TODO: Implement your business logic here
// This is a stub implementation for demonstration

}} // namespace {namespace.name}

// C wrapper factory implementations
extern "C" {{

// TODO: Implement C wrapper factory functions
// Example:
// void* IExample_Create() {{
//     return new {namespace.name}::ExampleImpl();
// }}

}}
"""

    def _generate_impl_cmake(self, idl_file: IDLFile) -> str:
        """Generate CMakeLists.txt for C implementation."""
        sources = []
        for namespace in idl_file.namespaces:
            sources.append(f"{namespace.name}_impl.cpp")

        sources_list = "\n    ".join(sources)

        return f"""cmake_minimum_required(VERSION 3.16)
project(CImplementation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(
    ${{CMAKE_CURRENT_SOURCE_DIR}}
    ${{CMAKE_CURRENT_SOURCE_DIR}}/../CWrapper
)

# Source files
set(SOURCES
    {sources_list}
)

# Create shared library
add_library(${{PROJECT_NAME}} SHARED ${{SOURCES}})

# Link with C wrapper
target_link_libraries(${{PROJECT_NAME}} PRIVATE CWrapper)

# Export symbols on Windows
if(WIN32)
    target_compile_definitions(${{PROJECT_NAME}} PRIVATE MINIMIDL_EXPORTS)
endif()

# Installation
install(TARGETS ${{PROJECT_NAME}}
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)
"""

    def _generate_c_build_script(self, project_name: str) -> str:
        """Generate C/C++ build script."""
        return f"""#!/bin/bash
# Build C wrapper and implementation

set -e

echo "Building C wrapper and implementation for {project_name}..."

# Create build directory
mkdir -p build_c
cd build_c

# Configure
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)

echo "C libraries built successfully!"
echo "Libraries are in: build_c/"
"""

    def _generate_swift_build_script(self, project_name: str) -> str:
        """Generate Swift build script."""
        return f"""#!/bin/bash
# Build Swift package

set -e

echo "Building Swift package for {project_name}..."

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
cd {project_name}
swift build -c release

echo "Swift package built successfully!"
echo "To run tests: cd {project_name} && swift test"
"""

    def _generate_project_readme(self, project_name: str, idl_file: IDLFile) -> str:
        """Generate comprehensive project README."""
        interfaces = []
        for namespace in idl_file.namespaces:
            for iface in namespace.interfaces:
                swift_name = iface.name[1:] if iface.name.startswith("I") else iface.name
                interfaces.append(f"- `{swift_name}` (from {namespace.name}::{iface.name})")

        interfaces_list = "\n".join(interfaces) if interfaces else "No interfaces defined"

        return f"""# {project_name} Swift Project

This project provides Swift bindings for the {project_name} API, generated from MinimIDL interface definitions.

## Project Structure

```
{project_name}/
├── CWrapper/           # C wrapper interface
├── CImplementation/    # C++ implementation stubs
├── {project_name}/     # Swift package
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
    .package(path: "path/to/{project_name}/{project_name}")
]
```

### Example Code

```swift
import {project_name}

// Create an instance
let instance = MyClass()

// Use the API
// TODO: Add your code here
```

## Available Classes

{interfaces_list}

## Example App

An example iOS/macOS app is provided in the `ExampleApp` directory. To run:

1. Open `ExampleApp/{project_name}Example.xcodeproj` in Xcode
2. Build and run

## Implementation Notes

The C++ implementation in `CImplementation/` contains stub code. You need to:

1. Implement the actual business logic in the `*_impl.cpp` files
2. Implement the C wrapper factory functions
3. Rebuild using `./build_c.sh`

## Testing

To run Swift tests:

```bash
cd {project_name}
swift test
```

## Generated by MinimIDL

This code was automatically generated. Do not edit the generated files in the Swift package.
"""

    def _generate_example_app(
        self, project_name: str, idl_file: IDLFile, project_dir: Path
    ) -> list[Path]:
        """Generate example iOS/macOS app."""
        generated = []
        
        app_dir = project_dir / "ExampleApp"
        app_dir.mkdir(exist_ok=True)

        # Generate ContentView.swift
        content_view = self._generate_content_view(project_name, idl_file)
        content_path = self._write_file(app_dir / "ContentView.swift", content_view)
        generated.append(content_path)

        # Generate App.swift
        app_swift = self._generate_app_swift(project_name)
        app_path = self._write_file(app_dir / f"{project_name}App.swift", app_swift)
        generated.append(app_path)

        # Generate example project file
        proj_content = self._generate_xcodeproj_stub(project_name)
        proj_path = self._write_file(
            app_dir / f"{project_name}Example.xcodeproj.md", proj_content
        )
        generated.append(proj_path)

        return generated

    def _generate_content_view(self, project_name: str, idl_file: IDLFile) -> str:
        """Generate SwiftUI ContentView."""
        return f"""import SwiftUI
import {project_name}

struct ContentView: View {{
    @State private var statusMessage = "Ready"
    
    var body: some View {{
        VStack(spacing: 20) {{
            Text("{project_name} Example")
                .font(.largeTitle)
                .padding()
            
            Text(statusMessage)
                .font(.body)
                .foregroundColor(.secondary)
            
            Button("Test API") {{
                testAPI()
            }}
            .buttonStyle(.borderedProminent)
            
            Spacer()
        }}
        .padding()
    }}
    
    func testAPI() {{
        // TODO: Add your API test code here
        statusMessage = "API test completed"
    }}
}}

struct ContentView_Previews: PreviewProvider {{
    static var previews: some View {{
        ContentView()
    }}
}}
"""

    def _generate_app_swift(self, project_name: str) -> str:
        """Generate SwiftUI App file."""
        return f"""import SwiftUI

@main
struct {project_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""

    def _generate_xcodeproj_stub(self, project_name: str) -> str:
        """Generate Xcode project instructions."""
        return f"""# Creating Xcode Project for {project_name} Example

To create an Xcode project for this example:

1. Open Xcode
2. Create a new project (File > New > Project)
3. Choose "App" template
4. Configure:
   - Product Name: {project_name}Example
   - Interface: SwiftUI
   - Language: Swift
5. Replace the generated ContentView.swift with the one in this directory
6. Replace the generated App file with {project_name}App.swift
7. Add the Swift package dependency:
   - File > Add Package Dependencies
   - Add local package from ../{project_name}
8. Build and run

Note: Ensure you've built the C libraries first using ../build_c.sh
"""

    def _write_file(self, path: Path, content: str) -> Path:
        """Write content to file.

        Args:
            path: File path
            content: File content

        Returns:
            Path to written file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        logger.debug(f"Wrote {path}")
        return path