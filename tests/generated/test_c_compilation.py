"""Test that generated C wrapper code compiles."""

import subprocess
from pathlib import Path

import pytest

from minimidl.generators.c_wrapper import CWrapperGenerator
from minimidl.parser import parse_idl_file


@pytest.mark.slow
class TestCCompilation:
    """Test C wrapper compilation."""

    @pytest.fixture(scope="class")
    def generated_c(self, tmp_path_factory):
        """Generate C wrapper for testing."""
        # Use complete.idl fixture
        idl_path = Path(__file__).parent.parent / "fixtures" / "complete.idl"
        ast = parse_idl_file(idl_path)
        
        output_dir = tmp_path_factory.mktemp("c_test")
        generator = CWrapperGenerator()
        generator.generate(ast, output_dir)
        
        return output_dir

    def test_c_header_compilation(self, generated_c):
        """Test that C headers compile."""
        headers = list(generated_c.glob("*_wrapper.h"))
        assert len(headers) > 0, "No C headers generated"
        
        for header in headers:
            # Create a simple C file that includes the header
            test_c = f"""
#include "{header.name}"
#include <stdio.h>

int main() {{
    printf("Header compiled successfully\\n");
    return 0;
}}
"""
            test_file = generated_c / "test_header.c"
            test_file.write_text(test_c)
            
            result = subprocess.run(
                ["cc", "-I", str(generated_c), "-c", str(test_file)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"C header {header} failed: {result.stderr}"
            
            # Cleanup
            test_file.unlink()
            obj_file = generated_c / "test_header.o"
            if obj_file.exists():
                obj_file.unlink()

    def test_cmake_build(self, generated_c):
        """Test CMake build for C wrapper."""
        if not (generated_c / "CMakeLists.txt").exists():
            pytest.skip("No CMakeLists.txt generated")
        
        build_dir = generated_c / "build"
        build_dir.mkdir(exist_ok=True)
        
        # Configure
        result = subprocess.run(
            ["cmake", ".."],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"CMake output:\n{result.stdout}")
            print(f"CMake errors:\n{result.stderr}")
        
        assert result.returncode == 0, "CMake configuration failed"
        
        # Build
        result = subprocess.run(
            ["make", "-j4"],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_c_wrapper_symbols(self, generated_c):
        """Test that C wrapper exports expected symbols."""
        # This would require building a shared library and checking exports
        # For now, just verify the .def file if it exists
        def_files = list(generated_c.glob("*.def"))
        
        if def_files:
            def_file = def_files[0]
            content = def_file.read_text()
            
            # Should have EXPORTS section
            assert "EXPORTS" in content
            
            # Should have some function exports
            lines = content.splitlines()
            export_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith(";")]
            exports = [l for l in export_lines if l != "EXPORTS"]
            
            assert len(exports) > 0, "No symbols exported"