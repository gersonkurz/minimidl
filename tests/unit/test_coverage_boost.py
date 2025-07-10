"""Tests specifically to boost coverage to 90%."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile

from minimidl.ast.nodes import (
    IDLFile, Namespace, Interface, Method, PrimitiveType,
    LiteralExpression, BinaryExpression, UnaryExpression,
    TypeRef, ArrayType, DictType, SetType, NullableType,
    Enum, EnumValue, Constant, ConstantValue, Typedef,
    ForwardDeclaration, Property, Parameter
)
from minimidl.ast.transformer import IDLTransformer
from minimidl.ast.serialization import save_ast, load_ast, ast_to_dict, dict_to_ast
from minimidl.parser import IDLParser
from minimidl.generators.swift import SwiftGenerator
from minimidl.generators.c_wrapper import CWrapperGenerator
from minimidl.generators.cpp import CppGenerator
from minimidl.cli import generate, validate, parse


class TestTransformerCoverage:
    """Tests for transformer coverage."""
    
    def test_transformer_edge_cases(self):
        """Test transformer edge cases."""
        transformer = IDLTransformer()
        
        # Test empty lists
        result = transformer.parameter_list(None)
        assert result == []
        
        result = transformer.parameter_list([])
        assert result == []
        
        # Test empty enum values
        result = transformer.enum_values([])
        assert result == []
        
        # Test expression with single item
        result = transformer.expression([LiteralExpression(value=42)])
        assert isinstance(result, LiteralExpression)
        assert result.value == 42


class TestParserCoverage:
    """Tests for parser coverage."""
    
    def test_parse_file_success(self, tmp_path):
        """Test successful file parsing."""
        idl_file = tmp_path / "test.idl"
        idl_file.write_text("""
        namespace Test {
            interface IExample {
                void DoSomething();
            }
        }
        """)
        
        parser = IDLParser()
        ast = parser.parse_file(str(idl_file))
        
        assert len(ast.namespaces) == 1
        assert ast.source_file == str(idl_file)
        
    def test_parse_error_handling(self):
        """Test parser error handling."""
        parser = IDLParser()
        
        # Invalid IDL should raise exception
        with pytest.raises(Exception):
            parser.parse("invalid { syntax")


class TestSwiftGeneratorCoverage:
    """Tests for Swift generator coverage."""
    
    def test_swift_conversion_helpers(self):
        """Test Swift conversion helper methods."""
        gen = SwiftGenerator()
        
        # Test parameter conversion
        param = Parameter(name="userId", type=PrimitiveType(name="int32_t"))
        swift_param = gen._swift_parameter(param)
        assert "userId: Int32" in swift_param
        
        # Test method conversion
        method = Method(
            name="GetUser",
            return_type=NullableType(inner_type=TypeRef(name="IUser")),
            parameters=[param]
        )
        gen.namespace_name = "API"
        swift_method = gen._swift_method(method)
        assert "func getUser" in swift_method
        assert "IUser?" in swift_method
        
        # Test property getter
        prop = Property(
            name="count",
            type=PrimitiveType(name="int32_t"),
            writable=False
        )
        getter = gen._swift_property_getter(prop)
        assert "var count: Int32" in getter
        
        # Test property setter
        prop_writable = Property(
            name="name",
            type=PrimitiveType(name="string_t"),
            writable=True
        )
        setter = gen._swift_property_setter(prop_writable)
        assert "set {" in setter or "didSet {" in setter


class TestCWrapperGeneratorCoverage:
    """Tests for C wrapper generator coverage."""
    
    def test_c_wrapper_helpers(self):
        """Test C wrapper helper methods."""
        gen = CWrapperGenerator()
        gen.namespace_name = "Test"
        
        # Test discriminator enum generation
        interfaces = [
            Interface(name="IUser", methods=[], properties=[]),
            Interface(name="IManager", methods=[], properties=[])
        ]
        enums = [
            Enum(name="Status", backing_type="int32_t", values=[])
        ]
        
        disc_enum = gen._generate_discriminator_enum(interfaces, enums)
        assert "Test_Type_IUser" in disc_enum
        assert "Test_Type_IManager" in disc_enum
        assert "Test_Type_Status" in disc_enum


class TestCLICoverage:
    """Tests for CLI coverage."""
    
    @patch('minimidl.cli.IDLParser')
    @patch('minimidl.cli.CppWorkflow')
    @patch('minimidl.cli.SwiftWorkflow')
    def test_generate_all_workflow(self, mock_swift, mock_cpp, mock_parser):
        """Test generate with all targets workflow."""
        # Setup mocks
        mock_ast = MagicMock()
        mock_parser.return_value.parse_file.return_value = mock_ast
        
        with tempfile.NamedTemporaryFile(suffix=".idl", delete=False) as f:
            idl_path = Path(f.name)
            idl_path.write_text("namespace Test { }")
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = Path(tmpdir)
                
                # Call generate with all targets
                generate(idl_path, target="all", output=output_path)
                
                # Check both workflows were called
                mock_cpp.return_value.generate.assert_called_once()
                mock_swift.return_value.generate.assert_called_once()
        finally:
            idl_path.unlink()
    
    @patch('minimidl.cli.IDLParser')
    @patch('minimidl.cli.CppGenerator')  
    def test_generate_cpp_only(self, mock_gen, mock_parser):
        """Test generate with C++ only."""
        # Setup mocks
        mock_ast = MagicMock()
        mock_parser.return_value.parse_file.return_value = mock_ast
        
        with tempfile.NamedTemporaryFile(suffix=".idl", delete=False) as f:
            idl_path = Path(f.name)
            idl_path.write_text("namespace Test { }")
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = Path(tmpdir)
                
                # Call generate
                generate(idl_path, target="cpp", output=output_path, workflow=False)
                
                # Check generator was called
                mock_gen.return_value.generate.assert_called_once_with(mock_ast, output_path)
        finally:
            idl_path.unlink()
    
    @patch('minimidl.cli.console')
    def test_validate_with_errors(self, mock_console):
        """Test validate with semantic errors."""
        with tempfile.NamedTemporaryFile(suffix=".idl", delete=False) as f:
            idl_path = Path(f.name) 
            # IDL with forward declaration that's never defined
            idl_path.write_text("""
            namespace Test {
                interface IForward;
                interface IUser {
                    IForward GetForward();
                }
            }
            """)
        
        try:
            with pytest.raises(SystemExit):
                validate(idl_path)
                
            # Check error was printed
            assert mock_console.print.called
        finally:
            idl_path.unlink()


class TestSerializationCoverage:
    """Tests for serialization coverage."""
    
    def test_serialization_functions(self, tmp_path):
        """Test all serialization functions."""
        # Create simple AST
        ast = IDLFile(namespaces=[
            Namespace(
                name="Test",
                interfaces=[
                    Interface(
                        name="IExample",
                        methods=[
                            Method(
                                name="DoIt",
                                return_type=PrimitiveType(name="void"),
                                parameters=[]
                            )
                        ],
                        properties=[]
                    )
                ]
            )
        ])
        
        # Test save_ast
        ast_file = tmp_path / "test.json"
        save_ast(ast, ast_file)
        assert ast_file.exists()
        
        # Test load_ast
        loaded = load_ast(ast_file)
        assert len(loaded.namespaces) == 1
        
        # Test ast_to_dict
        data = ast_to_dict(ast)
        assert "namespaces" in data
        
        # Test dict_to_ast
        reconstructed = dict_to_ast(data, IDLFile)
        assert len(reconstructed.namespaces) == 1