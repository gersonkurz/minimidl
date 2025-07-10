"""Simple tests to improve coverage."""

import pytest
from pathlib import Path
import tempfile

from minimidl import parse_idl
from minimidl.ast.transformer import IDLTransformer
from minimidl.ast.serialization import save_ast, load_ast, ast_to_dict, dict_to_ast
from minimidl.parser import IDLParser
from minimidl.generators.swift import SwiftGenerator
from minimidl.generators.c_wrapper import CWrapperGenerator
from minimidl.generators.cpp import CppGenerator
from minimidl.ast.nodes import *


class TestSimpleCoverage:
    """Simple tests to improve coverage."""
    
    def test_transformer_methods(self):
        """Test transformer methods directly."""
        transformer = IDLTransformer()
        
        # Test that methods exist and can be called
        assert hasattr(transformer, 'transform')
        
        # Test simple transformations
        from lark import Token
        
        # Test unary expression with two items (operator and operand)
        op = Token('MINUS', '-')
        val = LiteralExpression(value=5)
        result = transformer.unary_expr([op, val])
        assert isinstance(result, UnaryExpression)
        assert result.operator == '-'
        
        # Test void type
        void_token = Token('VOID', 'void')
        result = transformer.void_type(void_token)
        assert isinstance(result, PrimitiveType)
        assert result.name == 'void'
    
    def test_swift_helpers(self):
        """Test Swift generator helpers."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                ACTIVE = 0,
                IN_PROGRESS = 1,
                DONE = 2
            }
            interface IExample {
                Status GetStatus();
                void SetStatus(Status s);
                string_t[] GetTags();
                dict<string_t, int32_t> GetCounts();
                set<string_t> GetUniqueNames();
                int32_t? GetOptionalId();
            }
        }
        """
        ast = parse_idl(idl)
        
        gen = SwiftGenerator()
        output = Path(tempfile.mkdtemp())
        
        # This will exercise many code paths
        gen.generate(ast, output)
        
        # Check files were created
        swift_file = output / "Sources" / "Test" / "Test.swift"
        assert swift_file.exists()
        
        content = swift_file.read_text()
        assert "enum Status" in content
        assert "func getStatus()" in content
        assert "func setStatus(" in content
    
    def test_c_wrapper_helpers(self):
        """Test C wrapper generator helpers."""
        idl = """
        namespace API {
            interface IUser {
                string_t GetName();
                void SetName(string_t name);
                int32_t GetId();
            }
        }
        """
        ast = parse_idl(idl)
        
        gen = CWrapperGenerator()
        output = Path(tempfile.mkdtemp())
        
        # This will exercise many code paths
        gen.generate(ast, output)
        
        # Check files were created
        header = output / "include" / "api_wrapper.h"
        assert header.exists()
        
        content = header.read_text()
        assert "API_IUser_GetName" in content
        assert "API_IUser_SetName" in content
        assert "API_IUser_GetId" in content
    
    def test_cpp_helpers(self):
        """Test C++ generator helpers."""
        idl = """
        namespace Test {
            const int32_t MAX_VALUE = 100;
            
            typedef string_t Name;
            
            interface IForward;
            
            interface IExample {
                void Method();
                string_t name writable;
                int32_t count;
            }
        }
        """
        ast = parse_idl(idl)
        
        gen = CppGenerator()
        output = Path(tempfile.mkdtemp())
        
        # This will exercise many code paths
        gen.generate(ast, output)
        
        # Check files were created
        header = output / "include" / "test.hpp"
        assert header.exists()
        
        content = header.read_text()
        assert "constexpr int32_t MAX_VALUE = 100" in content
        assert "using Name = std::string" in content
        assert "class IForward;" in content
    
    def test_serialization_paths(self):
        """Test serialization code paths."""
        # Create a simple AST
        ast = IDLFile(namespaces=[
            Namespace(
                name="Test",
                interfaces=[
                    Interface(
                        name="ITest",
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
        
        # Test serialization
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        
        try:
            # Save and load
            save_ast(ast, path)
            loaded = load_ast(path)
            
            # Convert to/from dict
            data = ast_to_dict(ast)
            reconstructed = dict_to_ast(data, IDLFile)
            
            assert len(loaded.namespaces) == 1
            assert len(reconstructed.namespaces) == 1
        finally:
            path.unlink()
    
    def test_load_nonexistent(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_ast("/nonexistent/file.json")
    
    def test_parser_caching(self):
        """Test parser is cached."""
        from minimidl.parser.parser import get_parser
        
        parser1 = get_parser()
        parser2 = get_parser()
        assert parser1 is parser2