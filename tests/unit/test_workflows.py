"""Unit tests for workflow modules."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from minimidl.ast.nodes import IDLFile, Interface, Method, Namespace, PrimitiveType
from minimidl.workflows.cpp_workflow import CppWorkflow
from minimidl.workflows.swift_workflow import SwiftWorkflow


class TestCppWorkflow:
    """Test C++ workflow."""

    @pytest.fixture
    def simple_ast(self):
        """Create a simple AST for testing."""
        return IDLFile(
            namespaces=[
                Namespace(
                    name="Test",
                    interfaces=[
                        Interface(
                            name="IExample",
                            methods=[
                                Method(
                                    name="GetValue",
                                    return_type=PrimitiveType(name="int32_t"),
                                    parameters=[],
                                )
                            ],
                            properties=[],
                        )
                    ],
                    enums=[],
                    typedefs=[],
                    constants=[],
                    forward_declarations=[],
                )
            ]
        )

    def test_cpp_workflow_initialization(self):
        """Test C++ workflow initialization."""
        workflow = CppWorkflow()
        assert workflow.config == {}
        assert workflow.generator is not None

        workflow = CppWorkflow({"enum_class": True})
        assert workflow.config["enum_class"] is True

    def test_generate_project_structure(self, simple_ast, tmp_path):
        """Test C++ project structure generation."""
        workflow = CppWorkflow()
        files = workflow.generate_project(simple_ast, tmp_path)

        assert len(files) > 0
        
        # Check project directory structure
        project_dir = tmp_path / "Test"
        assert project_dir.exists()
        assert (project_dir / "include").exists()
        assert (project_dir / "src").exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / "docs").exists()
        
        # Check generated files
        assert (project_dir / "CMakeLists.txt").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "build.sh").exists()
        assert (project_dir / "src" / "example.cpp").exists()
        assert (project_dir / "tests" / "test_main.cpp").exists()

    def test_generate_cmake(self, simple_ast):
        """Test CMake file generation."""
        workflow = CppWorkflow()
        cmake_content = workflow._generate_cmake("TestProject", simple_ast)
        
        assert "cmake_minimum_required" in cmake_content
        assert "project(TestProject" in cmake_content
        assert "CMAKE_CXX_STANDARD 17" in cmake_content
        assert "add_library" in cmake_content
        assert "enable_testing()" in cmake_content

    def test_generate_readme(self, simple_ast):
        """Test README generation."""
        workflow = CppWorkflow()
        readme = workflow._generate_readme("TestProject", simple_ast)
        
        assert "# TestProject" in readme
        assert "Generated C++ API" in readme
        assert "## Building" in readme
        assert "./build.sh" in readme
        assert "Test::IExample" in readme

    def test_generate_example(self, simple_ast):
        """Test example code generation."""
        workflow = CppWorkflow()
        example = workflow._generate_example("TestProject", simple_ast)
        
        assert "#include <iostream>" in example
        assert '#include "Test.hpp"' in example  # Capitalized namespace name
        assert "int main()" in example
        assert "Test::IExample" in example

    def test_custom_project_name(self, simple_ast, tmp_path):
        """Test custom project name."""
        workflow = CppWorkflow()
        files = workflow.generate_project(simple_ast, tmp_path, "CustomName")
        
        project_dir = tmp_path / "CustomName"
        assert project_dir.exists()


class TestSwiftWorkflow:
    """Test Swift workflow."""

    @pytest.fixture
    def simple_ast(self):
        """Create a simple AST for testing."""
        return IDLFile(
            namespaces=[
                Namespace(
                    name="Test",
                    interfaces=[
                        Interface(
                            name="IExample",
                            methods=[
                                Method(
                                    name="GetValue",
                                    return_type=PrimitiveType(name="int32_t"),
                                    parameters=[],
                                )
                            ],
                            properties=[],
                        )
                    ],
                    enums=[],
                    typedefs=[],
                    constants=[],
                    forward_declarations=[],
                )
            ]
        )

    def test_swift_workflow_initialization(self):
        """Test Swift workflow initialization."""
        workflow = SwiftWorkflow()
        assert workflow.config == {}
        assert workflow.swift_generator is not None
        assert workflow.c_wrapper_generator is not None

    def test_generate_project_structure(self, simple_ast, tmp_path):
        """Test Swift project structure generation."""
        workflow = SwiftWorkflow()
        files = workflow.generate_project(simple_ast, tmp_path)

        assert len(files) > 0
        
        # Check project directory structure
        project_dir = tmp_path / "Test"
        assert project_dir.exists()
        assert (project_dir / "CWrapper").exists()
        assert (project_dir / "CImplementation").exists()
        assert (project_dir / "Test" / "Package.swift").exists()
        
        # Check build scripts
        assert (project_dir / "build_c.sh").exists()
        assert (project_dir / "build_swift.sh").exists()
        assert (project_dir / "README.md").exists()

    def test_generate_cpp_implementation(self, simple_ast, tmp_path):
        """Test C++ implementation stub generation."""
        workflow = SwiftWorkflow()
        impl_dir = tmp_path / "impl"
        impl_dir.mkdir()
        
        files = workflow._generate_cpp_implementation(simple_ast, impl_dir)
        
        assert len(files) > 0
        assert (impl_dir / "test_impl.hpp").exists()
        assert (impl_dir / "test_impl.cpp").exists()
        assert (impl_dir / "CMakeLists.txt").exists()

    def test_generate_impl_header(self):
        """Test implementation header generation."""
        workflow = SwiftWorkflow()
        namespace = MagicMock()
        namespace.name = "Test"
        namespace.interfaces = [
            MagicMock(name="IExample")
        ]
        
        header = workflow._generate_impl_header(namespace)
        
        assert '#pragma once' in header
        assert '#include "Test_wrapper.h"' in header  # Capitalized namespace name
        assert 'namespace Test' in header
        assert 'class ExampleImpl' in header

    def test_generate_build_scripts(self, simple_ast):
        """Test build script generation."""
        workflow = SwiftWorkflow()
        
        c_script = workflow._generate_c_build_script("TestProject")
        assert "#!/bin/bash" in c_script
        assert "Building C wrapper" in c_script
        assert "cmake .." in c_script
        
        swift_script = workflow._generate_swift_build_script("TestProject")
        assert "#!/bin/bash" in swift_script
        assert "Building Swift package" in swift_script
        assert "swift build" in swift_script

    def test_generate_example_app(self, simple_ast, tmp_path):
        """Test example app generation."""
        workflow = SwiftWorkflow()
        app_files = workflow._generate_example_app("TestProject", simple_ast, tmp_path)
        
        assert len(app_files) > 0
        
        # Check ContentView was created
        content_view_found = False
        for f in app_files:
            if "ContentView.swift" in str(f):
                content_view_found = True
                content = f.read_text()
                assert "import SwiftUI" in content
                assert "import TestProject" in content
                
        assert content_view_found