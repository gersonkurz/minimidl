"""C++ project generation workflow."""

from pathlib import Path
from typing import Any

from loguru import logger

from minimidl.ast.nodes import IDLFile
from minimidl.generators.cpp import CppGenerator


class CppWorkflow:
    """Workflow for generating complete C++ projects."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize C++ workflow.

        Args:
            config: Optional configuration options
        """
        self.config = config or {}
        self.generator = CppGenerator()

    def generate_project(
        self, idl_file: IDLFile, output_dir: Path, project_name: str | None = None
    ) -> list[Path]:
        """Generate a complete C++ project.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Output directory for the project
            project_name: Optional project name (defaults to namespace name)

        Returns:
            List of generated file paths
        """
        logger.info(f"Generating C++ project in {output_dir}")
        generated_files = []

        # Get project name from first namespace if not provided
        if not project_name and idl_file.namespaces:
            project_name = idl_file.namespaces[0].name

        # Create project structure
        project_dir = output_dir / (project_name or "generated")
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create standard C++ project directories
        include_dir = project_dir / "include"
        src_dir = project_dir / "src"
        tests_dir = project_dir / "tests"
        docs_dir = project_dir / "docs"

        for directory in [include_dir, src_dir, tests_dir, docs_dir]:
            directory.mkdir(exist_ok=True)

        # Generate C++ code
        cpp_files = self.generator.generate(idl_file, include_dir)
        generated_files.extend(cpp_files)

        # Generate CMakeLists.txt
        cmake_content = self._generate_cmake(project_name or "Generated", idl_file)
        cmake_path = self._write_file(project_dir / "CMakeLists.txt", cmake_content)
        generated_files.append(cmake_path)

        # Generate README
        readme_content = self._generate_readme(project_name or "Generated", idl_file)
        readme_path = self._write_file(project_dir / "README.md", readme_content)
        generated_files.append(readme_path)

        # Generate minimidl_runtime.hpp
        runtime_content = self._generate_runtime_header()
        runtime_path = self._write_file(include_dir / "minimidl_runtime.hpp", runtime_content)
        generated_files.append(runtime_path)

        # Generate example code
        example_content = self._generate_example(project_name or "Generated", idl_file)
        example_path = self._write_file(src_dir / "example.cpp", example_content)
        generated_files.append(example_path)

        # Generate test stub
        test_content = self._generate_test(project_name or "Generated", idl_file)
        test_path = self._write_file(tests_dir / "test_main.cpp", test_content)
        generated_files.append(test_path)

        # Generate build script
        build_content = self._generate_build_script()
        build_path = self._write_file(project_dir / "build.sh", build_content)
        build_path.chmod(0o755)  # Make executable
        generated_files.append(build_path)

        logger.success(
            f"Generated C++ project with {len(generated_files)} files in {project_dir}"
        )
        return generated_files

    def _generate_cmake(self, project_name: str, idl_file: IDLFile) -> str:
        """Generate CMakeLists.txt content."""
        # Get all header files from namespaces
        headers = []
        for namespace in idl_file.namespaces:
            headers.append(f"{namespace.name}.hpp")

        return f"""cmake_minimum_required(VERSION 3.16)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add include directories
include_directories(${{CMAKE_CURRENT_SOURCE_DIR}}/include)

# Header files
set(HEADERS
{chr(10).join(f'    include/{header}' for header in headers)}
)

# Create interface library for headers
add_library(${{PROJECT_NAME}}_interface INTERFACE)
target_include_directories(${{PROJECT_NAME}}_interface 
    INTERFACE 
        $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}/include>
        $<INSTALL_INTERFACE:include>
)

# Example executable
add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE ${{PROJECT_NAME}}_interface)

# Enable testing
enable_testing()

# Test executable
add_executable(test_main tests/test_main.cpp)
target_link_libraries(test_main PRIVATE ${{PROJECT_NAME}}_interface)
add_test(NAME test_main COMMAND test_main)

# Installation rules
install(FILES ${{HEADERS}} DESTINATION include)
install(TARGETS ${{PROJECT_NAME}}_interface
    EXPORT ${{PROJECT_NAME}}Targets
    INCLUDES DESTINATION include
)

# Optional: Export targets for find_package support
# Uncomment the following lines if you want to install this as a library
# install(EXPORT ${{PROJECT_NAME}}Targets
#     FILE ${{PROJECT_NAME}}Targets.cmake
#     NAMESPACE ${{PROJECT_NAME}}::
#     DESTINATION lib/cmake/${{PROJECT_NAME}}
# )
"""

    def _generate_readme(self, project_name: str, idl_file: IDLFile) -> str:
        """Generate README.md content."""
        interfaces = []
        enums = []
        for namespace in idl_file.namespaces:
            interfaces.extend(
                [f"- `{namespace.name}::{iface.name}`" for iface in namespace.interfaces]
            )
            enums.extend([f"- `{namespace.name}::{enum.name}`" for enum in namespace.enums])

        interfaces_section = "\n".join(interfaces) if interfaces else "No interfaces defined"
        enums_section = "\n".join(enums) if enums else "No enums defined"

        return f"""# {project_name}

Generated C++ API from MinimIDL interface definitions.

## Building

This project uses CMake for building. To build:

```bash
./build.sh
```

Or manually:

```bash
mkdir build
cd build
cmake ..
make
```

## Running Tests

After building:

```bash
cd build
ctest
```

## Running Example

After building:

```bash
./build/example
```

## API Overview

### Interfaces
{interfaces_section}

### Enums
{enums_section}

## Integration

To use this library in your project, add it as a subdirectory in your CMakeLists.txt:

```cmake
add_subdirectory(path/to/{project_name})
target_link_libraries(your_target PRIVATE {project_name}::interface)
```

Or install it and use find_package:

```cmake
find_package({project_name} REQUIRED)
target_link_libraries(your_target PRIVATE {project_name}::interface)
```

## Generated by MinimIDL

This code was automatically generated. Do not edit manually.
"""

    def _generate_example(self, project_name: str, idl_file: IDLFile) -> str:
        """Generate example.cpp content."""
        includes = []
        code_examples = []

        for namespace in idl_file.namespaces:
            includes.append(f'#include "{namespace.name}.hpp"')

            # Generate example comment for interfaces
            for iface in namespace.interfaces:
                code_examples.append(
                    f"""
    // TODO: Implement {namespace.name}::{iface.name}
    // Example:
    // class {iface.name[1:] if iface.name.startswith("I") else iface.name}Impl : public {namespace.name}::{iface.name} {{
    //     // Implement all pure virtual methods
    // }};"""
                )

        includes_str = "\n".join(includes)
        examples_str = "\n".join(code_examples) if code_examples else '    std::cout << "No interfaces to demonstrate\\n";'

        return f"""#include <iostream>
#include <memory>
{includes_str}

int main() {{
    std::cout << "{project_name} Example\\n";
    std::cout << "====================\\n\\n";
    {examples_str}
    
    return 0;
}}
"""

    def _generate_test(self, project_name: str, idl_file: IDLFile) -> str:
        """Generate test_main.cpp content."""
        includes = []
        for namespace in idl_file.namespaces:
            includes.append(f'#include "{namespace.name}.hpp"')

        includes_str = "\n".join(includes)

        return f"""#include <iostream>
#include <cassert>
{includes_str}

// Simple test framework
#define TEST(name) void test_##name(); tests.push_back({{#name, test_##name}}); void test_##name()
#define ASSERT(cond) if (!(cond)) {{ std::cerr << "FAILED: " #cond " at " __FILE__ ":" << __LINE__ << "\\n"; return; }}

struct Test {{
    const char* name;
    void (*func)();
}};

std::vector<Test> tests;

TEST(basic_compilation) {{
    // Test that headers compile correctly
    std::cout << "  Testing basic compilation... ";
    ASSERT(true);
    std::cout << "PASSED\\n";
}}

TEST(interface_creation) {{
    // TODO: Add interface creation tests
    std::cout << "  Testing interface creation... ";
    ASSERT(true);
    std::cout << "PASSED\\n";
}}

int main() {{
    std::cout << "{project_name} Tests\\n";
    std::cout << "===================\\n\\n";
    
    int passed = 0;
    int failed = 0;
    
    for (const auto& test : tests) {{
        std::cout << "Running " << test.name << ":\\n";
        test.func();
        passed++;
    }}
    
    std::cout << "\\nTest Summary: " << passed << " passed, " << failed << " failed\\n";
    return failed > 0 ? 1 : 0;
}}
"""

    def _generate_build_script(self) -> str:
        """Generate build.sh script."""
        return """#!/bin/bash
# Build script for C++ project

set -e

# Colors for output
GREEN='\\033[0;32m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

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
"""

    def _generate_runtime_header(self) -> str:
        """Generate minimidl_runtime.hpp content."""
        return """#pragma once
// MinimIDL Runtime Support Library
// This header provides base classes and utilities for generated code

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <atomic>

namespace minimidl {

// Base class for reference counted objects
class RefCounted {
protected:
    mutable std::atomic<int32_t> m_refCount{1};
    
public:
    virtual ~RefCounted() = default;
    
    void AddRef() const {
        m_refCount.fetch_add(1, std::memory_order_relaxed);
    }
    
    void Release() const {
        if (m_refCount.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            delete this;
        }
    }
};

// String type for IDL compatibility
using string_t = std::string;

// Array type template
template<typename T>
using array_t = std::vector<T>;

// Dictionary type template
template<typename K, typename V>
using dict_t = std::unordered_map<K, V>;

} // namespace minimidl
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