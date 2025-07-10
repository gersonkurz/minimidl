"""Unit tests for CLI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from minimidl.cli import app, version_callback
from minimidl.ast.nodes import IDLFile


class TestCLI:
    """Test CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def sample_idl_file(self, tmp_path):
        """Create a sample IDL file."""
        idl_content = """
namespace Test {
    interface IExample {
        string_t GetName();
    }
}
"""
        idl_file = tmp_path / "test.idl"
        idl_file.write_text(idl_content)
        return idl_file

    def test_version_callback(self):
        """Test version callback."""
        from typer import Exit
        with pytest.raises(Exit):
            version_callback(True)
        
        # Should not raise when False
        version_callback(False)

    def test_cli_no_args(self, runner):
        """Test CLI with no arguments shows help."""
        result = runner.invoke(app)
        assert result.exit_code == 2  # no_args_is_help=True causes exit code 2
        assert "Usage:" in result.output  # Just check for usage, not specific format

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "MinimIDL version" in result.output

    def test_parse_command(self, runner, sample_idl_file):
        """Test parse command."""
        result = runner.invoke(app, ["parse", str(sample_idl_file)])
        assert result.exit_code == 0
        assert "Successfully parsed" in result.output
        assert "Test" in result.output

    def test_parse_json_output(self, runner, sample_idl_file):
        """Test parse command with JSON output."""
        result = runner.invoke(app, ["parse", str(sample_idl_file), "--json"])
        assert result.exit_code == 0
        assert '"namespaces"' in result.output

    def test_parse_json_to_file(self, runner, sample_idl_file, tmp_path):
        """Test parse command with JSON output to file."""
        output_file = tmp_path / "ast.json"
        result = runner.invoke(
            app, ["parse", str(sample_idl_file), "--json", "-o", str(output_file)]
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert "AST written to" in result.output

    def test_parse_nonexistent_file(self, runner):
        """Test parse command with non-existent file."""
        result = runner.invoke(app, ["parse", "nonexistent.idl"])
        assert result.exit_code == 1
        assert "does not exist" in result.output

    def test_validate_command(self, runner, sample_idl_file):
        """Test validate command."""
        result = runner.invoke(app, ["validate", str(sample_idl_file)])
        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_validate_invalid_file(self, runner, tmp_path):
        """Test validate command with invalid IDL."""
        bad_idl = tmp_path / "bad.idl"
        bad_idl.write_text("invalid idl content")
        
        result = runner.invoke(app, ["validate", str(bad_idl)])
        assert result.exit_code == 1
        assert "Error:" in result.output

    @patch("minimidl.cli.CppWorkflow")
    def test_generate_cpp(self, mock_workflow, runner, sample_idl_file, tmp_path):
        """Test generate command with C++ target."""
        mock_instance = MagicMock()
        mock_instance.generate_project.return_value = [tmp_path / "test.hpp"]
        mock_workflow.return_value = mock_instance
        
        result = runner.invoke(
            app, 
            ["generate", str(sample_idl_file), "--target", "cpp", "-o", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Generated" in result.output
        assert "CPP files" in result.output

    @patch("minimidl.cli.SwiftWorkflow")
    def test_generate_swift(self, mock_workflow, runner, sample_idl_file, tmp_path):
        """Test generate command with Swift target."""
        mock_instance = MagicMock()
        mock_instance.generate_project.return_value = [tmp_path / "test.swift"]
        mock_workflow.return_value = mock_instance
        
        result = runner.invoke(
            app,
            ["generate", str(sample_idl_file), "--target", "swift", "-o", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Generated" in result.output
        assert "SWIFT files" in result.output

    @patch("minimidl.cli.CWrapperGenerator")
    def test_generate_c_direct(self, mock_gen, runner, sample_idl_file, tmp_path):
        """Test generate command with C target (direct generator)."""
        mock_instance = MagicMock()
        mock_instance.generate.return_value = [tmp_path / "test.h"]
        mock_gen.return_value = mock_instance
        
        result = runner.invoke(
            app,
            ["generate", str(sample_idl_file), "--target", "c", "-o", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Generated" in result.output

    def test_generate_all_targets(self, runner, sample_idl_file, tmp_path):
        """Test generate command with all targets."""
        with patch("minimidl.cli.CppWorkflow") as mock_cpp, \
             patch("minimidl.cli.CWrapperGenerator") as mock_c, \
             patch("minimidl.cli.SwiftWorkflow") as mock_swift:
            
            # Setup mocks
            for mock in [mock_cpp, mock_c, mock_swift]:
                instance = MagicMock()
                instance.generate.return_value = [tmp_path / "test"]
                instance.generate_project.return_value = [tmp_path / "test"]
                mock.return_value = instance
            
            result = runner.invoke(
                app,
                ["generate", str(sample_idl_file), "--target", "all", "-o", str(tmp_path)]
            )
            assert result.exit_code == 0
            assert "CPP files" in result.output
            assert "C files" in result.output
            assert "SWIFT files" in result.output

    def test_generate_invalid_target(self, runner, sample_idl_file):
        """Test generate command with invalid target."""
        result = runner.invoke(
            app,
            ["generate", str(sample_idl_file), "--target", "invalid"]
        )
        assert result.exit_code == 1
        assert "Unknown target" in result.output

    def test_generate_with_ast_caching(self, runner, sample_idl_file, tmp_path):
        """Test generate command with AST caching."""
        with patch("minimidl.cli.save_ast") as mock_save:
            with patch("minimidl.cli.CppWorkflow") as mock_workflow:
                mock_instance = MagicMock()
                mock_instance.generate_project.return_value = []
                mock_workflow.return_value = mock_instance
                
                result = runner.invoke(
                    app,
                    ["generate", str(sample_idl_file), "--cache-ast", "-o", str(tmp_path)]
                )
                assert result.exit_code == 0
                assert "AST cached" in result.output
                mock_save.assert_called_once()

    def test_generate_from_ast(self, runner, tmp_path):
        """Test generate command from cached AST."""
        # Create a mock AST file
        ast_file = tmp_path / "test.ast"
        ast_file.write_text('{"namespaces": []}')
        
        with patch("minimidl.cli.load_ast") as mock_load:
            mock_load.return_value = IDLFile(namespaces=[])
            
            with patch("minimidl.cli.CppWorkflow") as mock_workflow:
                mock_instance = MagicMock()
                mock_instance.generate_project.return_value = []
                mock_workflow.return_value = mock_instance
                
                result = runner.invoke(
                    app,
                    ["generate", "--from-ast", str(ast_file), "-o", str(tmp_path)]
                )
                assert result.exit_code == 0

    def test_generate_no_input(self, runner):
        """Test generate command with no input file."""
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 1
        assert "Either provide an IDL file" in result.output

    def test_verbose_mode(self, runner, sample_idl_file):
        """Test verbose mode."""
        with patch("minimidl.cli.logger") as mock_logger:
            result = runner.invoke(
                app, ["--verbose", "parse", str(sample_idl_file)]
            )
            assert result.exit_code == 0
            # Verbose mode should configure logger
            mock_logger.remove.assert_called()
            mock_logger.add.assert_called()

    def test_parse_with_validation_errors(self, runner, tmp_path):
        """Test parse with validation errors."""
        # Create IDL with validation error
        bad_idl = tmp_path / "bad.idl"
        bad_idl.write_text("""
namespace Test {
    interface IExample {
        UnknownType GetValue();
    }
}
""")
        
        with patch("minimidl.cli.SemanticValidator") as mock_validator:
            mock_instance = MagicMock()
            mock_instance.validate.return_value = ["Unknown type 'UnknownType'"]
            mock_validator.return_value = mock_instance
            
            result = runner.invoke(app, ["parse", str(bad_idl)])
            assert result.exit_code == 1
            assert "Validation errors" in result.output