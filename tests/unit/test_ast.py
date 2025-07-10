"""Unit tests for AST nodes and transformation."""

import pytest

from minimidl import IDLFile, parse_idl
from minimidl.ast.nodes import (
    ArrayType,
    BinaryExpression,
    Constant,
    DictType,
    Enum,
    EnumValue,
    ForwardDeclaration,
    IdentifierExpression,
    Interface,
    LiteralExpression,
    Method,
    Namespace,
    NullableType,
    Parameter,
    PrimitiveType,
    Property,
    SetType,
    TypeRef,
    Typedef,
)


class TestASTTransformation:
    """Test AST transformation from parsed IDL."""

    def test_simple_namespace(self) -> None:
        """Test basic namespace AST transformation."""
        idl = "namespace Test {}"
        ast = parse_idl(idl)
        
        assert isinstance(ast, IDLFile)
        assert len(ast.namespaces) == 1
        assert ast.namespaces[0].name == "Test"
        assert len(ast.namespaces[0].interfaces) == 0

    def test_interface_with_methods(self) -> None:
        """Test interface with methods transformation."""
        idl = """
        namespace Test {
            interface ICalculator {
                double Add(double a, double b);
                void Clear();
            }
        }
        """
        ast = parse_idl(idl)
        
        assert len(ast.namespaces) == 1
        ns = ast.namespaces[0]
        assert len(ns.interfaces) == 1
        
        iface = ns.interfaces[0]
        assert iface.name == "ICalculator"
        assert len(iface.methods) == 2
        
        # Check Add method
        add_method = iface.methods[0]
        assert add_method.name == "Add"
        assert isinstance(add_method.return_type, PrimitiveType)
        assert add_method.return_type.name == "double"
        assert len(add_method.parameters) == 2
        assert add_method.parameters[0].name == "a"
        assert add_method.parameters[1].name == "b"
        
        # Check Clear method
        clear_method = iface.methods[1]
        assert clear_method.name == "Clear"
        assert clear_method.return_type.name == "void"
        assert len(clear_method.parameters) == 0

    def test_interface_with_properties(self) -> None:
        """Test interface with properties transformation."""
        idl = """
        namespace Test {
            interface IConfig {
                int32_t Count;
                string_t Name writable;
                bool IsEnabled;
            }
        }
        """
        ast = parse_idl(idl)
        
        iface = ast.namespaces[0].interfaces[0]
        assert len(iface.properties) == 3
        
        # Check Count property
        count_prop = iface.properties[0]
        assert count_prop.name == "Count"
        assert isinstance(count_prop.type, PrimitiveType)
        assert count_prop.type.name == "int32_t"
        assert not count_prop.writable
        
        # Check Name property
        name_prop = iface.properties[1]
        assert name_prop.name == "Name"
        assert name_prop.type.name == "string_t"
        assert name_prop.writable
        
        # Check IsEnabled property
        enabled_prop = iface.properties[2]
        assert enabled_prop.name == "IsEnabled"
        assert enabled_prop.type.name == "bool"
        assert not enabled_prop.writable

    def test_enum_transformation(self) -> None:
        """Test enum transformation."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                UNKNOWN = 0,
                ACTIVE = 1,
                INACTIVE = 2
            }
        }
        """
        ast = parse_idl(idl)
        
        ns = ast.namespaces[0]
        assert len(ns.enums) == 1
        
        enum = ns.enums[0]
        assert enum.name == "Status"
        assert enum.backing_type == "int32_t"
        assert len(enum.values) == 3
        
        # Check enum values
        assert enum.values[0].name == "UNKNOWN"
        assert isinstance(enum.values[0].value, LiteralExpression)
        assert enum.values[0].value.value == 0
        
        assert enum.values[1].name == "ACTIVE"
        assert enum.values[1].value.value == 1
        
        assert enum.values[2].name == "INACTIVE"
        assert enum.values[2].value.value == 2

    def test_typedef_transformation(self) -> None:
        """Test typedef transformation."""
        idl = """
        namespace Test {
            typedef int32_t UserId;
            typedef string_t[] NameList;
        }
        """
        ast = parse_idl(idl)
        
        ns = ast.namespaces[0]
        assert len(ns.typedefs) == 2
        
        # Check UserId typedef
        user_id = ns.typedefs[0]
        assert user_id.name == "UserId"
        assert isinstance(user_id.type, PrimitiveType)
        assert user_id.type.name == "int32_t"
        
        # Check NameList typedef
        name_list = ns.typedefs[1]
        assert name_list.name == "NameList"
        assert isinstance(name_list.type, ArrayType)
        assert isinstance(name_list.type.element_type, PrimitiveType)
        assert name_list.type.element_type.name == "string_t"

    def test_constant_transformation(self) -> None:
        """Test constant transformation."""
        idl = """
        namespace Test {
            const int32_t MAX_SIZE = 100;
            const int32_t FLAGS = 0xFF;
            const int32_t SHIFTED = (1 << 8);
        }
        """
        ast = parse_idl(idl)
        
        ns = ast.namespaces[0]
        assert len(ns.constants) == 3
        
        # Check MAX_SIZE
        max_size = ns.constants[0]
        assert max_size.name == "MAX_SIZE"
        assert max_size.constant_value.type == "int32_t"
        assert isinstance(max_size.constant_value.value, LiteralExpression)
        assert max_size.constant_value.value.value == 100
        
        # Check FLAGS
        flags = ns.constants[1]
        assert flags.name == "FLAGS"
        assert flags.constant_value.value.value == 0xFF
        assert flags.constant_value.value.base == "hex"
        
        # Check SHIFTED
        shifted = ns.constants[2]
        assert shifted.name == "SHIFTED"
        # Should be a binary expression inside parentheses
        assert isinstance(shifted.constant_value.value, BinaryExpression)
        assert shifted.constant_value.value.operator == "<<"
        assert shifted.constant_value.value.left.value == 1  # type: ignore[attr-defined]
        assert shifted.constant_value.value.right.value == 8  # type: ignore[attr-defined]

    def test_forward_declaration(self) -> None:
        """Test forward declaration transformation."""
        idl = """
        namespace Test {
            interface IForward;
            interface IUser {
                IForward GetForward();
            }
        }
        """
        ast = parse_idl(idl)
        
        ns = ast.namespaces[0]
        assert len(ns.forward_declarations) == 1
        assert ns.forward_declarations[0].name == "IForward"
        
        assert len(ns.interfaces) == 1
        iface = ns.interfaces[0]
        assert iface.name == "IUser"
        
        method = iface.methods[0]
        assert isinstance(method.return_type, TypeRef)
        assert method.return_type.name == "IForward"

    def test_nullable_types(self) -> None:
        """Test nullable type transformation."""
        idl = """
        namespace Test {
            interface INullable {
                string_t? GetOptionalString();
                IUser? FindUser(string_t name);
            }
        }
        """
        ast = parse_idl(idl)
        
        iface = ast.namespaces[0].interfaces[0]
        
        # Check GetOptionalString
        method1 = iface.methods[0]
        assert isinstance(method1.return_type, NullableType)
        assert isinstance(method1.return_type.inner_type, PrimitiveType)
        assert method1.return_type.inner_type.name == "string_t"
        
        # Check FindUser
        method2 = iface.methods[1]
        assert isinstance(method2.return_type, NullableType)
        assert isinstance(method2.return_type.inner_type, TypeRef)
        assert method2.return_type.inner_type.name == "IUser"

    def test_array_types(self) -> None:
        """Test array type transformation."""
        idl = """
        namespace Test {
            interface IArrays {
                int32_t[] GetNumbers();
                string_t[] GetNames();
                IUser[] GetUsers();
            }
        }
        """
        ast = parse_idl(idl)
        
        iface = ast.namespaces[0].interfaces[0]
        
        # Check all methods return array types
        for method in iface.methods:
            assert isinstance(method.return_type, ArrayType)
        
        # Check element types
        assert iface.methods[0].return_type.element_type.name == "int32_t"  # type: ignore[attr-defined]
        assert iface.methods[1].return_type.element_type.name == "string_t"  # type: ignore[attr-defined]
        assert iface.methods[2].return_type.element_type.name == "IUser"  # type: ignore[attr-defined]

    def test_dict_types(self) -> None:
        """Test dictionary type transformation."""
        idl = """
        namespace Test {
            interface IDicts {
                dict<int32_t, string_t> GetMapping();
                dict<string_t, IUser> GetUserMap();
            }
        }
        """
        ast = parse_idl(idl)
        
        iface = ast.namespaces[0].interfaces[0]
        
        # Check GetMapping
        method1 = iface.methods[0]
        assert isinstance(method1.return_type, DictType)
        assert method1.return_type.key_type.name == "int32_t"  # type: ignore[attr-defined]
        assert method1.return_type.value_type.name == "string_t"  # type: ignore[attr-defined]
        
        # Check GetUserMap
        method2 = iface.methods[1]
        assert isinstance(method2.return_type, DictType)
        assert method2.return_type.key_type.name == "string_t"  # type: ignore[attr-defined]
        assert method2.return_type.value_type.name == "IUser"  # type: ignore[attr-defined]

    def test_set_types(self) -> None:
        """Test set type transformation."""
        idl = """
        namespace Test {
            interface ISets {
                set<int32_t> GetUniqueNumbers();
                set<string_t> GetUniqueNames();
            }
        }
        """
        ast = parse_idl(idl)
        
        iface = ast.namespaces[0].interfaces[0]
        
        # Check both methods return set types
        for method in iface.methods:
            assert isinstance(method.return_type, SetType)
        
        assert iface.methods[0].return_type.element_type.name == "int32_t"  # type: ignore[attr-defined]
        assert iface.methods[1].return_type.element_type.name == "string_t"  # type: ignore[attr-defined]

    def test_complex_expressions(self) -> None:
        """Test complex expression transformation."""
        idl = """
        namespace Test {
            enum Flags : int32_t {
                NONE = 0,
                READ = (1 << 0),
                WRITE = (1 << 1),
                EXECUTE = (1 << 2),
                ALL = (1 << 3) - 1
            }
        }
        """
        ast = parse_idl(idl)
        
        enum = ast.namespaces[0].enums[0]
        
        # Check NONE
        assert enum.values[0].value.value == 0  # type: ignore[attr-defined]
        
        # Check bit shift expressions
        for i in range(1, 4):
            val = enum.values[i].value
            assert isinstance(val, BinaryExpression)
            assert val.operator == "<<"
            assert val.left.value == 1  # type: ignore[attr-defined]
            assert val.right.value == i - 1  # type: ignore[attr-defined]
        
        # Check ALL = (1 << 3) - 1
        all_val = enum.values[4].value
        assert isinstance(all_val, BinaryExpression)
        assert all_val.operator == "-"
        assert isinstance(all_val.left, BinaryExpression)
        assert all_val.left.operator == "<<"
        assert all_val.right.value == 1  # type: ignore[attr-defined]

    def test_line_column_tracking(self) -> None:
        """Test that line and column information is preserved."""
        idl = """namespace Test {
    interface IUser {
        string_t GetName();
    }
}"""
        ast = parse_idl(idl)
        
        # Namespace should be on line 1
        ns = ast.namespaces[0]
        assert ns.line == 1
        
        # Interface should be on line 2
        iface = ns.interfaces[0]
        assert iface.line == 2
        
        # Method should be on line 3
        method = iface.methods[0]
        assert method.line == 3


class TestASTNodeValidation:
    """Test AST node validation."""

    def test_primitive_type_validation(self) -> None:
        """Test primitive type validation."""
        # Valid primitive types
        for type_name in ["bool", "int32_t", "int64_t", "float", "double", "string_t"]:
            prim = PrimitiveType(name=type_name)
            assert prim.name == type_name
        
        # Invalid primitive type
        with pytest.raises(ValueError, match="Invalid primitive type"):
            PrimitiveType(name="invalid_type")

    def test_enum_backing_type_validation(self) -> None:
        """Test enum backing type validation."""
        # Valid backing types
        for backing in ["int32_t", "int64_t"]:
            enum = Enum(name="Test", backing_type=backing)
            assert enum.backing_type == backing
        
        # Invalid backing type
        with pytest.raises(ValueError, match="Invalid enum backing type"):
            Enum(name="Test", backing_type="float")

    def test_constant_type_validation(self) -> None:
        """Test constant type validation."""
        # Valid constant types
        for const_type in ["int32_t", "int64_t", "float", "double"]:
            const_val = ConstantValue(
                type=const_type, 
                value=LiteralExpression(value=0)
            )
            assert const_val.type == const_type
        
        # Invalid constant type
        with pytest.raises(ValueError, match="Invalid constant type"):
            ConstantValue(type="string_t", value=LiteralExpression(value=0))


class TestComplexIDLExamples:
    """Test complex IDL examples from CLAUDE.md."""

    def test_basic_interface_example(self) -> None:
        """Test the basic interface example from CLAUDE.md."""
        idl = """// Basic interface
namespace TestAPI {
    interface IUser {
        string_t GetName();
        void SetName(string_t name);
        int32_t Age;
        bool IsActive writable;
    }
}"""
        ast = parse_idl(idl)
        
        assert len(ast.namespaces) == 1
        ns = ast.namespaces[0]
        assert ns.name == "TestAPI"
        
        iface = ns.interfaces[0]
        assert iface.name == "IUser"
        assert len(iface.methods) == 2
        assert len(iface.properties) == 2
        
        # Check methods
        assert iface.methods[0].name == "GetName"
        assert iface.methods[1].name == "SetName"
        
        # Check properties
        assert iface.properties[0].name == "Age"
        assert not iface.properties[0].writable
        assert iface.properties[1].name == "IsActive"
        assert iface.properties[1].writable

    def test_complex_example_with_all_features(self) -> None:
        """Test the complex example with all features from CLAUDE.md."""
        idl = """// Complex example with all features
namespace ComplexAPI {
    const int32_t MAX_USERS = 0xFF;
    const int32_t FLAGS = (1 << 8);
    
    typedef int32_t UserId;
    
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
    }
    
    interface IUserManager {
        IUser[] GetUsers();
        IUser? FindUser(UserId id);
        void AddUser(IUser user);
    }
}"""
        ast = parse_idl(idl)
        
        ns = ast.namespaces[0]
        assert ns.name == "ComplexAPI"
        
        # Check constants
        assert len(ns.constants) == 2
        assert ns.constants[0].name == "MAX_USERS"
        assert ns.constants[1].name == "FLAGS"
        
        # Check typedef
        assert len(ns.typedefs) == 1
        assert ns.typedefs[0].name == "UserId"
        
        # Check enum
        assert len(ns.enums) == 1
        assert ns.enums[0].name == "Status"
        
        # Check forward declaration
        assert len(ns.forward_declarations) == 1
        assert ns.forward_declarations[0].name == "IUserManager"
        
        # Check interfaces
        assert len(ns.interfaces) == 2
        
        # Check IUser interface
        iuser = ns.interfaces[0]
        assert iuser.name == "IUser"
        assert len(iuser.methods) == 6
        
        # Check return types
        assert isinstance(iuser.methods[0].return_type, TypeRef)  # UserId
        assert isinstance(iuser.methods[1].return_type, NullableType)  # string_t?
        assert isinstance(iuser.methods[2].return_type, TypeRef)  # Status
        assert isinstance(iuser.methods[3].return_type, TypeRef)  # IUserManager
        assert isinstance(iuser.methods[4].return_type, ArrayType)  # string_t[]
        assert isinstance(iuser.methods[5].return_type, DictType)  # dict<...>
        
        # Check IUserManager interface
        imngr = ns.interfaces[1]
        assert imngr.name == "IUserManager"
        assert len(imngr.methods) == 3