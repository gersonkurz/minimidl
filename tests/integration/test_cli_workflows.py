"""Integration tests for CLI workflows."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def sample_idl(tmp_path: Path) -> Path:
    """Create a sample IDL file for testing."""
    idl_content = """
namespace TestAPI {
    enum ErrorCode : int32_t {
        OK = 0,
        ERROR = 1,
        NOT_FOUND = 2
    }
    
    interface IService {
        string_t GetVersion();
        void SetConfig(string_t key, string_t value);
        ErrorCode Process(int32_t id);
        string_t config writable;
    }
    
    interface IManager {
        IService? GetService(string_t name);
        string_t[] ListServices();
    }
}
"""
    idl_file = tmp_path / "test.idl"
    idl_file.write_text(idl_content)
    return idl_file


class TestCLIWorkflows:
    """Test CLI workflow integration."""

    def run_minimidl(self, *args: str) -> subprocess.CompletedProcess:
        """Run minimidl CLI command."""
        cmd = ["python", "-m", "minimidl.cli"] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_parse_workflow(self, sample_idl: Path) -> None:
        """Test parsing workflow."""
        # Test basic parse
        result = self.run_minimidl("parse", str(sample_idl))
        assert result.returncode == 0
        assert "Successfully parsed" in result.stdout
        assert "TestAPI" in result.stdout

        # Test JSON output
        result = self.run_minimidl("parse", str(sample_idl), "--json")
        assert result.returncode == 0
        assert '"namespaces"' in result.stdout

    def test_validate_workflow(self, sample_idl: Path) -> None:
        """Test validation workflow."""
        result = self.run_minimidl("validate", str(sample_idl))
        assert result.returncode == 0
        assert "is valid" in result.stdout

    def test_cpp_generation_workflow(self, sample_idl: Path, tmp_path: Path) -> None:
        """Test C++ project generation workflow."""
        output_dir = tmp_path / "cpp_output"
        
        result = self.run_minimidl(
            "generate", str(sample_idl), 
            "--target", "cpp",
            "--output", str(output_dir)
        )
        
        assert result.returncode == 0
        assert "Generated" in result.stdout
        assert "CPP files" in result.stdout
        
        # Check generated project structure
        project_dir = output_dir / "TestAPI"
        assert project_dir.exists()
        assert (project_dir / "CMakeLists.txt").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "build.sh").exists()
        assert (project_dir / "include" / "testapi.hpp").exists()

    def test_swift_generation_workflow(self, sample_idl: Path, tmp_path: Path) -> None:
        """Test Swift project generation workflow."""
        output_dir = tmp_path / "swift_output"
        
        result = self.run_minimidl(
            "generate", str(sample_idl),
            "--target", "swift",
            "--output", str(output_dir)
        )
        
        assert result.returncode == 0
        assert "Generated" in result.stdout
        assert "SWIFT files" in result.stdout
        
        # Check generated project structure
        project_dir = output_dir / "TestAPI"
        assert project_dir.exists()
        assert (project_dir / "TestAPI" / "Package.swift").exists()
        assert (project_dir / "CWrapper").exists()
        assert (project_dir / "CImplementation").exists()

    def test_ast_caching_workflow(self, sample_idl: Path, tmp_path: Path) -> None:
        """Test AST caching workflow."""
        output_dir = tmp_path / "cached_output"
        ast_file = tmp_path / "test.ast"
        
        # Generate with AST caching
        result = self.run_minimidl(
            "generate", str(sample_idl),
            "--target", "cpp",
            "--output", str(output_dir),
            "--cache-ast",
            "--ast-file", str(ast_file)
        )
        
        assert result.returncode == 0
        assert ast_file.exists()
        assert "AST cached" in result.stdout
        
        # Generate from cached AST
        output_dir2 = tmp_path / "from_ast"
        result = self.run_minimidl(
            "generate",
            "--from-ast", str(ast_file),
            "--target", "swift",
            "--output", str(output_dir2)
        )
        
        assert result.returncode == 0
        assert "Generated" in result.stdout

    def test_all_targets_workflow(self, sample_idl: Path, tmp_path: Path) -> None:
        """Test generating all targets."""
        output_dir = tmp_path / "all_output"
        
        result = self.run_minimidl(
            "generate", str(sample_idl),
            "--target", "all",
            "--output", str(output_dir)
        )
        
        assert result.returncode == 0
        assert "CPP files" in result.stdout
        assert "C files" in result.stdout
        assert "SWIFT files" in result.stdout
        
        # Check that multiple outputs were generated
        assert (output_dir / "TestAPI").exists()  # C++ project
        assert (output_dir / "testapi_wrapper.h").exists()  # C wrapper
        
    def test_error_handling(self, tmp_path: Path) -> None:
        """Test error handling in workflows."""
        # Test with non-existent file
        result = self.run_minimidl("parse", "nonexistent.idl")
        assert result.returncode == 1
        assert "does not exist" in result.stdout
        
        # Test with invalid IDL
        bad_idl = tmp_path / "bad.idl"
        bad_idl.write_text("this is not valid IDL")
        
        result = self.run_minimidl("parse", str(bad_idl))
        assert result.returncode == 1
        assert "Error" in result.stdout

    def test_verbose_logging(self, sample_idl: Path, tmp_path: Path) -> None:
        """Test verbose logging."""
        output_dir = tmp_path / "verbose_output"
        
        result = self.run_minimidl(
            "--verbose",
            "generate", str(sample_idl),
            "--target", "cpp",
            "--output", str(output_dir)
        )
        
        assert result.returncode == 0
        # Check for debug messages in stderr
        assert "DEBUG" in result.stderr or "Parsing" in result.stderr