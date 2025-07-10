"""Unit tests for AST serialization and deserialization."""

import json
import tempfile
from pathlib import Path

import pytest

from minimidl import IDLFile, load_ast, parse_idl, save_ast
from minimidl.ast.serialization import ast_to_dict, dict_to_ast


class TestSerialization:
    """Test AST serialization to/from JSON."""

    def test_simple_round_trip(self) -> None:
        """Test round-trip serialization of a simple IDL."""
        idl = """
        namespace Test {
            interface IUser {
                string_t GetName();
            }
        }
        """
        # Parse to AST
        ast1 = parse_idl(idl)

        # Convert to dict and back
        data = ast_to_dict(ast1)
        ast2 = dict_to_ast(data, IDLFile)

        # Compare
        assert ast1 == ast2
        assert ast1.namespaces[0].name == ast2.namespaces[0].name
        assert len(ast1.namespaces[0].interfaces) == len(ast2.namespaces[0].interfaces)

    def test_file_serialization(self) -> None:
        """Test saving and loading AST from file."""
        idl = """
        namespace Test {
            interface ICalculator {
                double Add(double a, double b);
                double Subtract(double a, double b);
            }
        }
        """
        ast1 = parse_idl(idl)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            save_ast(ast1, temp_path)

            # Verify file exists and is valid JSON
            assert temp_path.exists()
            with open(temp_path) as f:
                data = json.load(f)
            assert "namespaces" in data

            # Load back
            ast2 = load_ast(temp_path)

            # Compare
            assert ast1 == ast2
        finally:
            temp_path.unlink()

    def test_complex_serialization(self) -> None:
        """Test serialization of complex IDL with all features."""
        idl = """
        namespace ComplexAPI {
            const int32_t MAX_USERS = 0xFF;
            const int32_t FLAGS = (1 << 8);
            
            typedef int32_t UserId;
            typedef string_t[] NameList;
            
            enum Status : int32_t {
                UNKNOWN = 0,
                ACTIVE = 1,
                INACTIVE = 2
            }
            
            interface IUserManager;
            
            interface IUser {
                UserId GetId();
                string_t? GetOptionalName();
                Status GetStatus();
                IUserManager GetManager();
                string_t[] GetTags();
                dict<string_t, string_t> GetProperties();
                set<int32_t> GetPermissions();
                
                int32_t UserCount;
                string_t DefaultName writable;
            }
            
            interface IUserManager {
                IUser[] GetUsers();
                IUser? FindUser(UserId id);
                void AddUser(IUser user);
            }
        }
        """
        ast1 = parse_idl(idl)

        # Round trip through JSON
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            save_ast(ast1, temp_path)
            ast2 = load_ast(temp_path)

            # Deep comparison
            assert len(ast1.namespaces) == len(ast2.namespaces)

            ns1 = ast1.namespaces[0]
            ns2 = ast2.namespaces[0]

            assert ns1.name == ns2.name
            assert len(ns1.constants) == len(ns2.constants)
            assert len(ns1.typedefs) == len(ns2.typedefs)
            assert len(ns1.enums) == len(ns2.enums)
            assert len(ns1.interfaces) == len(ns2.interfaces)
            assert len(ns1.forward_declarations) == len(ns2.forward_declarations)

            # Check specific elements
            assert ns1.constants[0].name == ns2.constants[0].name
            assert ns1.typedefs[0].name == ns2.typedefs[0].name
            assert ns1.enums[0].name == ns2.enums[0].name
            assert ns1.interfaces[0].name == ns2.interfaces[0].name

            # Check method preservation
            iface1 = ns1.interfaces[0]
            iface2 = ns2.interfaces[0]
            assert len(iface1.methods) == len(iface2.methods)
            assert len(iface1.properties) == len(iface2.properties)

            # Check nullable type preservation
            method1 = iface1.methods[1]  # GetOptionalName
            method2 = iface2.methods[1]
            assert method1.name == method2.name
            assert (
                type(method1.return_type).__name__ == type(method2.return_type).__name__
            )

        finally:
            temp_path.unlink()

    def test_expression_serialization(self) -> None:
        """Test serialization of various expression types."""
        idl = """
        namespace Test {
            const int32_t DECIMAL = 42;
            const int32_t HEX = 0xFF;
            const int32_t BINARY = 0b1010;
            const int32_t SHIFT = (1 << 8);
            const int32_t COMPLEX = ((1 << 8) | 0xFF) & 0xF0F0;
        }
        """
        ast1 = parse_idl(idl)

        # Serialize and deserialize
        data = ast_to_dict(ast1)
        ast2 = dict_to_ast(data, IDLFile)

        # Verify all constants are preserved
        ns1 = ast1.namespaces[0]
        ns2 = ast2.namespaces[0]

        assert len(ns1.constants) == len(ns2.constants)
        for c1, c2 in zip(ns1.constants, ns2.constants):
            assert c1.name == c2.name
            assert c1.constant_value.type == c2.constant_value.type

    def test_source_file_preservation(self) -> None:
        """Test that source_file attribute is preserved."""
        idl = "namespace Test {}"

        # Create AST with source file
        ast1 = parse_idl(idl)
        ast1.source_file = "/path/to/test.idl"

        # Round trip
        data = ast_to_dict(ast1)
        ast2 = dict_to_ast(data, IDLFile)

        assert ast2.source_file == "/path/to/test.idl"

    def test_position_information_excluded(self) -> None:
        """Test that line/column information is included in JSON."""
        idl = """
        namespace Test {
            interface IUser {
                string_t GetName();
            }
        }
        """
        ast = parse_idl(idl)

        # Convert to dict
        data = ast_to_dict(ast)

        # Check that position info is included in JSON
        # Top-level has no position
        assert data.get("line") is None
        assert data.get("column") is None

        # Check nested objects have position
        ns_data = data["namespaces"][0]
        assert "line" in ns_data
        assert "column" in ns_data
        assert ns_data["line"] == 2

    def test_load_nonexistent_file(self) -> None:
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError, match="AST file not found"):
            load_ast("/nonexistent/path/file.json")

    def test_load_invalid_json(self) -> None:
        """Test loading invalid JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)
            f.write(b"invalid json{")

        try:
            with pytest.raises(json.JSONDecodeError):
                load_ast(temp_path)
        finally:
            temp_path.unlink()

    def test_load_invalid_ast_structure(self) -> None:
        """Test loading JSON with invalid AST structure."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)
            # Write valid JSON but invalid AST structure
            f.write(b'{"invalid": "structure"}')

        try:
            with pytest.raises(ValueError):
                load_ast(temp_path)
        finally:
            temp_path.unlink()

    def test_parent_directory_creation(self) -> None:
        """Test that save_ast creates parent directories."""
        idl = "namespace Test {}"
        ast = parse_idl(idl)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to save in non-existent subdirectory
            path = Path(tmpdir) / "subdir" / "nested" / "ast.json"

            save_ast(ast, path)

            # Verify file was created
            assert path.exists()

            # Verify it can be loaded
            ast2 = load_ast(path)
            assert ast == ast2
