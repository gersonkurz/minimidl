"""Test that generated C++ code compiles."""

import subprocess
from pathlib import Path

import pytest

from minimidl.parser import parse_idl_file
from minimidl.workflows.cpp_workflow import CppWorkflow


@pytest.mark.slow
class TestCppCompilation:
    """Test C++ code compilation."""

    @pytest.fixture(scope="class")
    def generated_cpp(self, tmp_path_factory):
        """Generate C++ code for testing."""
        # Use complete.idl fixture
        idl_path = Path(__file__).parent.parent / "fixtures" / "complete.idl"
        ast = parse_idl_file(idl_path)
        
        output_dir = tmp_path_factory.mktemp("cpp_test")
        workflow = CppWorkflow()
        workflow.generate_project(ast, output_dir)
        
        return output_dir / "Complete"

    def test_cmake_configure(self, generated_cpp):
        """Test CMake configuration."""
        build_dir = generated_cpp / "build"
        build_dir.mkdir()
        
        result = subprocess.run(
            ["cmake", ".."],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"CMake failed: {result.stderr}"
        assert (build_dir / "CMakeCache.txt").exists()

    def test_cpp_compilation(self, generated_cpp):
        """Test C++ compilation."""
        # First configure
        build_dir = generated_cpp / "build"
        if not build_dir.exists():
            build_dir.mkdir()
            subprocess.run(["cmake", ".."], cwd=build_dir, check=True)
        
        # Then build
        result = subprocess.run(
            ["make", "-j4"],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        # Check for compilation errors
        if result.returncode != 0:
            print(f"Build output:\n{result.stdout}")
            print(f"Build errors:\n{result.stderr}")
        
        assert result.returncode == 0, "C++ compilation failed"

    def test_generated_headers_valid(self, generated_cpp):
        """Test that generated headers are valid C++."""
        include_dir = generated_cpp / "include"
        
        # Find all generated headers
        headers = list(include_dir.glob("*.hpp"))
        assert len(headers) > 0, "No headers generated"
        
        # Try to compile each header standalone
        for header in headers:
            test_cpp = f"""
#include "{header.name}"

int main() {{
    return 0;
}}
"""
            test_file = generated_cpp / "test_header.cpp"
            test_file.write_text(test_cpp)
            
            result = subprocess.run(
                ["c++", "-std=c++17", "-I", str(include_dir), "-c", str(test_file)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Header {header} failed to compile: {result.stderr}"
            
            # Cleanup
            test_file.unlink()
            obj_file = generated_cpp / "test_header.o"
            if obj_file.exists():
                obj_file.unlink()