"""Unit tests for AST semantic validation."""

import pytest

from minimidl import parse_idl
from minimidl.ast import ValidationError, validate_ast


class TestSemanticValidation:
    """Test semantic validation of AST."""

    def test_valid_idl(self) -> None:
        """Test validation of valid IDL."""
        idl = """
        namespace Test {
            interface IUser {
                string_t GetName();
                void SetName(string_t name);
            }
        }
        """
        ast = parse_idl(idl)
        # Should not raise
        validate_ast(ast)

    def test_unknown_type_reference(self) -> None:
        """Test detection of unknown type references."""
        idl = """
        namespace Test {
            interface IUser {
                UnknownType GetSomething();
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'UnknownType'"):
            validate_ast(ast)

    def test_forward_declaration_resolution(self) -> None:
        """Test that forward declarations are properly resolved."""
        idl = """
        namespace Test {
            interface IManager;
            
            interface IUser {
                IManager GetManager();
            }
            
            interface IManager {
                IUser[] GetUsers();
            }
        }
        """
        ast = parse_idl(idl)
        # Should not raise - forward declaration is resolved
        validate_ast(ast)

    def test_unresolved_forward_declaration(self) -> None:
        """Test detection of unresolved forward declarations."""
        idl = """
        namespace Test {
            interface IManager;
            
            interface IUser {
                IManager GetManager();
                IUnknown GetUnknown();  // Not declared
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'IUnknown'"):
            validate_ast(ast)

    def test_duplicate_interface_names(self) -> None:
        """Test detection of duplicate interface names."""
        idl = """
        namespace Test {
            interface IUser {
                string_t GetName();
            }
            
            interface IUser {  // Duplicate
                int32_t GetId();
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Duplicate type definition: IUser"):
            validate_ast(ast)

    def test_duplicate_method_names(self) -> None:
        """Test detection of duplicate method names in interface."""
        idl = """
        namespace Test {
            interface IUser {
                string_t GetName();
                int32_t GetName();  // Duplicate method name
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Duplicate method name 'GetName'"):
            validate_ast(ast)

    def test_duplicate_property_names(self) -> None:
        """Test detection of duplicate property names in interface."""
        idl = """
        namespace Test {
            interface IUser {
                string_t Name;
                int32_t Name;  // Duplicate property name
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Duplicate property name 'Name'"):
            validate_ast(ast)

    def test_method_property_name_conflict(self) -> None:
        """Test detection of method/property name conflicts."""
        idl = """
        namespace Test {
            interface IUser {
                string_t GetName();
                int32_t GetName;  // Property with same name as method
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(
            ValidationError, match="Property 'GetName' conflicts with method name"
        ):
            validate_ast(ast)

    def test_duplicate_parameter_names(self) -> None:
        """Test detection of duplicate parameter names."""
        idl = """
        namespace Test {
            interface ICalculator {
                double Add(double value, double value);  // Duplicate param name
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Duplicate parameter name 'value'"):
            validate_ast(ast)

    def test_duplicate_enum_values(self) -> None:
        """Test detection of duplicate enum values."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                ACTIVE = 1,
                INACTIVE = 2,
                ACTIVE = 3  // Duplicate
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Duplicate enum value 'ACTIVE'"):
            validate_ast(ast)

    def test_typedef_with_unknown_type(self) -> None:
        """Test typedef referencing unknown type."""
        idl = """
        namespace Test {
            typedef UnknownType MyType;
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'UnknownType'"):
            validate_ast(ast)

    def test_complex_type_validation(self) -> None:
        """Test validation of complex nested types."""
        idl = """
        namespace Test {
            interface IUser {
                dict<string_t, UnknownType> GetMapping();
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'UnknownType'"):
            validate_ast(ast)

    def test_array_of_unknown_type(self) -> None:
        """Test array of unknown type."""
        idl = """
        namespace Test {
            interface IUser {
                UnknownType[] GetItems();
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'UnknownType'"):
            validate_ast(ast)

    def test_nullable_unknown_type(self) -> None:
        """Test nullable unknown type."""
        idl = """
        namespace Test {
            interface IUser {
                UnknownType? GetOptional();
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'UnknownType'"):
            validate_ast(ast)

    def test_cross_namespace_type_reference(self) -> None:
        """Test that types from different namespaces are isolated."""
        idl = """
        namespace First {
            interface IUser {
                string_t GetName();
            }
        }
        
        namespace Second {
            interface IManager {
                IUser GetUser();  // Should fail - IUser is in different namespace
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError, match="Unknown type 'IUser'"):
            validate_ast(ast)

    def test_enum_and_typedef_references(self) -> None:
        """Test that enums and typedefs can be referenced."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                ACTIVE = 1,
                INACTIVE = 0
            }
            
            typedef int32_t UserId;
            
            interface IUser {
                Status GetStatus();
                UserId GetId();
            }
        }
        """
        ast = parse_idl(idl)
        # Should not raise - enum and typedef are valid types
        validate_ast(ast)

    def test_void_return_type(self) -> None:
        """Test that void is accepted as return type."""
        idl = """
        namespace Test {
            interface IUser {
                void Clear();
                void Reset();
            }
        }
        """
        ast = parse_idl(idl)
        # Should not raise - void is valid return type
        validate_ast(ast)

    def test_multiple_errors_reported(self) -> None:
        """Test that multiple errors are collected and reported."""
        idl = """
        namespace Test {
            interface IUser {
                UnknownType1 GetFirst();
                UnknownType2 GetSecond();
                void Process(UnknownType3 param);
            }
        }
        """
        ast = parse_idl(idl)

        with pytest.raises(ValidationError) as exc_info:
            validate_ast(ast)

        error_msg = str(exc_info.value)
        assert "3 error(s)" in error_msg
        assert "UnknownType1" in error_msg
        assert "UnknownType2" in error_msg
        assert "UnknownType3" in error_msg
