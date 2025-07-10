"""Additional parser tests for better coverage."""

import pytest
from lark import LarkError

from minimidl.parser import IDLParser
from minimidl.parser.parser import get_parser


class TestParserCoverage:
    """Additional parser tests for coverage."""

    def test_get_parser_caching(self):
        """Test that parser is cached."""
        parser1 = get_parser()
        parser2 = get_parser()
        assert parser1 is parser2  # Same instance

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = IDLParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.idl")

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = IDLParser()
        
        # Empty content should parse to empty AST
        ast = parser.parse("")
        assert len(ast.namespaces) == 0

    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only content."""
        parser = IDLParser()
        
        ast = parser.parse("   \n\t\n   ")
        assert len(ast.namespaces) == 0

    def test_parse_comments_only(self):
        """Test parsing comments-only content."""
        parser = IDLParser()
        
        idl = """
        // This is a comment
        /* This is a
           multiline comment */
        // Another comment
        """
        ast = parser.parse(idl)
        assert len(ast.namespaces) == 0

    def test_parse_syntax_error(self):
        """Test parsing with syntax error."""
        parser = IDLParser()
        
        # Missing semicolon
        idl = """
        namespace Test {
            interface IExample {
                void Method()  // Missing semicolon
            }
        }
        """
        
        with pytest.raises(LarkError):
            parser.parse(idl)

    def test_parse_invalid_token(self):
        """Test parsing with invalid token."""
        parser = IDLParser()
        
        # Invalid character
        idl = """
        namespace Test {
            interface IExample {
                void Method();
                @invalid_token
            }
        }
        """
        
        with pytest.raises(LarkError):
            parser.parse(idl)

    def test_parse_unclosed_brace(self):
        """Test parsing with unclosed brace."""
        parser = IDLParser()
        
        idl = """
        namespace Test {
            interface IExample {
                void Method();
            // Missing closing brace
        }
        """
        
        with pytest.raises(LarkError):
            parser.parse(idl)

    def test_parse_duplicate_semicolon(self):
        """Test parsing with duplicate semicolons."""
        parser = IDLParser()
        
        # This should parse successfully
        idl = """
        namespace Test {
            interface IExample {
                void Method();;  // Double semicolon
            }
        }
        """
        
        ast = parser.parse(idl)
        assert len(ast.namespaces) == 1

    def test_parse_complex_expressions(self):
        """Test parsing complex constant expressions."""
        parser = IDLParser()
        
        idl = """
        namespace Test {
            const int32_t A = 1 + 2 * 3;
            const int32_t B = (1 + 2) * 3;
            const int32_t C = 1 << 8 | 0xFF;
            const int32_t D = ~0xFF & 0x0F;
        }
        """
        
        ast = parser.parse(idl)
        assert len(ast.namespaces[0].constants) == 4

    def test_parse_nested_types(self):
        """Test parsing nested collection types."""
        parser = IDLParser()
        
        idl = """
        namespace Test {
            interface IComplex {
                dict<string_t, string_t[]> GetNestedDict();
                set<dict<string_t, int32_t>> GetSetOfDicts();
                string_t[][]? GetOptionalMatrix();
            }
        }
        """
        
        ast = parser.parse(idl)
        iface = ast.namespaces[0].interfaces[0]
        assert len(iface.methods) == 3

    def test_parse_multiple_namespaces(self):
        """Test parsing multiple namespaces."""
        parser = IDLParser()
        
        idl = """
        namespace First {
            interface IFirst {
                void MethodOne();
            }
        }
        
        namespace Second {
            interface ISecond {
                void MethodTwo();
            }
        }
        """
        
        ast = parser.parse(idl)
        assert len(ast.namespaces) == 2
        assert ast.namespaces[0].name == "First"
        assert ast.namespaces[1].name == "Second"

    def test_parse_all_primitive_types(self):
        """Test parsing all primitive types."""
        parser = IDLParser()
        
        idl = """
        namespace Test {
            interface ITypes {
                void TestVoid();
                bool TestBool();
                int32_t TestInt32();
                int64_t TestInt64();
                float TestFloat();
                double TestDouble();
                string_t TestString();
            }
        }
        """
        
        ast = parser.parse(idl)
        iface = ast.namespaces[0].interfaces[0]
        assert len(iface.methods) == 7

    def test_parse_enum_edge_cases(self):
        """Test enum parsing edge cases."""
        parser = IDLParser()
        
        # Enum with trailing comma
        idl = """
        namespace Test {
            enum Status : int32_t {
                ACTIVE = 0,
                INACTIVE = 1,  // Trailing comma
            }
        }
        """
        
        ast = parser.parse(idl)
        enum = ast.namespaces[0].enums[0]
        assert len(enum.values) == 2

    def test_parse_writable_variations(self):
        """Test different writable property syntaxes."""
        parser = IDLParser()
        
        idl = """
        namespace Test {
            interface IProps {
                string_t readonly;
                string_t name writable;
                int32_t count writable;
            }
        }
        """
        
        ast = parser.parse(idl)
        props = ast.namespaces[0].interfaces[0].properties
        assert len(props) == 3
        assert not props[0].writable
        assert props[1].writable
        assert props[2].writable