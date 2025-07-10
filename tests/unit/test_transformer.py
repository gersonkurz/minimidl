"""Unit tests for AST transformer module."""

import pytest
from lark import Token, Tree

from minimidl.ast.nodes import (
    ArrayType, BinaryExpression, Constant, ConstantValue, DictType,
    Enum, EnumValue, ForwardDeclaration, Interface, LiteralExpression,
    Method, Namespace, NullableType, Parameter, PrimitiveType, Property,
    SetType, Typedef, TypeRef, UnaryExpression
)
from minimidl.ast.transformer import IDLTransformer


class TestIDLTransformer:
    """Test IDL transformer methods."""

    def test_namespace_transformation(self):
        """Test namespace transformation."""
        transformer = IDLTransformer()
        
        # Create mock tree structure
        name_token = Token('IDENTIFIER', 'TestAPI')
        name_token.line = 1
        name_token.column = 10
        
        interface = Interface(
            name="ITest",
            methods=[],
            properties=[]
        )
        
        result = transformer.namespace([name_token, [interface], [], [], [], []])
        
        assert isinstance(result, Namespace)
        assert result.name == "TestAPI"
        assert len(result.interfaces) == 1
        assert result.interfaces[0].name == "ITest"
        assert result.line == 1
        assert result.column == 10

    def test_interface_transformation(self):
        """Test interface transformation."""
        transformer = IDLTransformer()
        
        name_token = Token('IDENTIFIER', 'IUser')
        name_token.line = 2
        name_token.column = 15
        
        method = Method(
            name="GetName",
            return_type=PrimitiveType(name="string_t"),
            parameters=[]
        )
        
        result = transformer.interface([name_token, [method]])
        
        assert isinstance(result, Interface)
        assert result.name == "IUser"
        assert len(result.methods) == 1
        assert result.methods[0].name == "GetName"

    def test_method_transformation(self):
        """Test method transformation."""
        transformer = IDLTransformer()
        
        return_type = PrimitiveType(name="string_t")
        name_token = Token('IDENTIFIER', 'GetValue')
        name_token.line = 3
        name_token.column = 20
        
        param = Parameter(
            name="id",
            type=PrimitiveType(name="int32_t")
        )
        
        result = transformer.method_decl([return_type, name_token, [param]])
        
        assert isinstance(result, Method)
        assert result.name == "GetValue"
        assert isinstance(result.return_type, PrimitiveType)
        assert result.return_type.name == "string_t"
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "id"

    def test_property_transformation(self):
        """Test property transformation."""
        transformer = IDLTransformer()
        
        type_spec = PrimitiveType(name="string_t")
        name_token = Token('IDENTIFIER', 'name')
        name_token.line = 4
        name_token.column = 25
        
        # Test read-only property
        result = transformer.property_decl([type_spec, name_token])
        assert isinstance(result, Property)
        assert result.name == "name"
        assert result.writable is False
        
        # Test writable property
        result = transformer.property_decl([type_spec, name_token, True])
        assert result.writable is True

    def test_enum_transformation(self):
        """Test enum transformation."""
        transformer = IDLTransformer()
        
        name_token = Token('IDENTIFIER', 'Status')
        name_token.line = 5
        name_token.column = 30
        
        backing_type = Token('IDENTIFIER', 'int32_t')
        
        enum_val = EnumValue(
            name="ACTIVE",
            value=LiteralExpression(value=1)
        )
        
        result = transformer.enum_decl([name_token, backing_type, [enum_val]])
        
        assert isinstance(result, Enum)
        assert result.name == "Status"
        assert result.backing_type == "int32_t"
        assert len(result.values) == 1
        assert result.values[0].name == "ACTIVE"

    def test_typedef_transformation(self):
        """Test typedef transformation."""
        transformer = IDLTransformer()
        
        type_spec = PrimitiveType(name="int32_t")
        name_token = Token('IDENTIFIER', 'UserId')
        name_token.line = 6
        name_token.column = 35
        
        result = transformer.typedef_decl([type_spec, name_token])
        
        assert isinstance(result, Typedef)
        assert result.name == "UserId"
        assert isinstance(result.type, PrimitiveType)
        assert result.type.name == "int32_t"

    def test_constant_transformation(self):
        """Test constant transformation."""
        transformer = IDLTransformer()
        
        type_token = PrimitiveType(name="int32_t")
        name_token = Token('IDENTIFIER', 'MAX_SIZE')
        name_token.line = 7
        name_token.column = 40
        
        value = LiteralExpression(value=100)
        
        result = transformer.const_decl([type_token, name_token, value])
        
        assert isinstance(result, Constant)
        assert result.name == "MAX_SIZE"
        assert result.constant_value.type == "int32_t"
        assert result.constant_value.value.value == 100

    def test_type_transformations(self):
        """Test various type transformations."""
        transformer = IDLTransformer()
        
        # Test primitive type
        prim_token = Token('IDENTIFIER', 'string_t')
        result = transformer.primitive_type(prim_token)
        assert isinstance(result, PrimitiveType)
        assert result.name == "string_t"
        
        # Test type reference
        ref_token = Token('IDENTIFIER', 'IUser')
        result = transformer.type_ref(ref_token)
        assert isinstance(result, TypeRef)
        assert result.name == "IUser"
        
        # Test array type
        element = PrimitiveType(name="int32_t")
        result = transformer.array_type([element])
        assert isinstance(result, ArrayType)
        assert result.element_type.name == "int32_t"
        
        # Test dict type
        key_type = PrimitiveType(name="string_t")
        value_type = PrimitiveType(name="int32_t")
        result = transformer.dict_type([key_type, value_type])
        assert isinstance(result, DictType)
        assert result.key_type.name == "string_t"
        assert result.value_type.name == "int32_t"
        
        # Test set type
        element = PrimitiveType(name="string_t")
        result = transformer.set_type([element])
        assert isinstance(result, SetType)
        assert result.element_type.name == "string_t"
        
        # Test nullable type
        inner = PrimitiveType(name="string_t")
        result = transformer.nullable_type([inner])
        assert isinstance(result, NullableType)
        assert result.inner_type.name == "string_t"

    def test_expression_transformations(self):
        """Test expression transformations."""
        transformer = IDLTransformer()
        
        # Test decimal number
        token = Token('DECIMAL_NUMBER', '42')
        result = transformer.decimal_number(token)
        assert isinstance(result, LiteralExpression)
        assert result.value == 42
        assert result.base is None
        
        # Test hex number
        token = Token('HEX_NUMBER', '0xFF')
        result = transformer.hex_number(token)
        assert isinstance(result, LiteralExpression)
        assert result.value == 255
        assert result.base == "hex"
        
        # Test binary number
        token = Token('BINARY_NUMBER', '0b1010')
        result = transformer.binary_number(token)
        assert isinstance(result, LiteralExpression)
        assert result.value == 10
        assert result.base == "binary"
        
        # Test unary expression
        op_token = Token('MINUS', '-')
        operand = LiteralExpression(value=5)
        result = transformer.unary_expr([op_token, operand])
        assert isinstance(result, UnaryExpression)
        assert result.operator == "-"
        assert result.operand.value == 5

    def test_binary_expressions(self):
        """Test binary expression transformations."""
        transformer = IDLTransformer()
        
        # Test addition
        left = LiteralExpression(value=5)
        op = Token('PLUS', '+')
        right = LiteralExpression(value=3)
        
        result = transformer.add_expr([left, op, right])
        assert isinstance(result, BinaryExpression)
        assert result.operator == "+"
        assert result.left.value == 5
        assert result.right.value == 3
        
        # Test multiplication
        left = LiteralExpression(value=4)
        op = Token('STAR', '*')
        right = LiteralExpression(value=2)
        
        result = transformer.mul_expr([left, op, right])
        assert isinstance(result, BinaryExpression)
        assert result.operator == "*"
        
        # Test bit shift
        left = LiteralExpression(value=1)
        op = Token('LSHIFT', '<<')
        right = LiteralExpression(value=8)
        
        result = transformer.shift_expr([left, op, right])
        assert isinstance(result, BinaryExpression)
        assert result.operator == "<<"

    def test_forward_declaration(self):
        """Test forward declaration transformation."""
        transformer = IDLTransformer()
        
        name_token = Token('IDENTIFIER', 'IForward')
        name_token.line = 10
        name_token.column = 50
        
        result = transformer.forward_decl([name_token])
        
        assert isinstance(result, ForwardDeclaration)
        assert result.name == "IForward"
        assert result.line == 10
        assert result.column == 50

    def test_parameter_transformation(self):
        """Test parameter transformation."""
        transformer = IDLTransformer()
        
        type_spec = PrimitiveType(name="int32_t")
        name_token = Token('IDENTIFIER', 'count')
        
        result = transformer.parameter([type_spec, name_token])
        
        assert isinstance(result, Parameter)
        assert result.name == "count"
        assert isinstance(result.type, PrimitiveType)
        assert result.type.name == "int32_t"

    def test_enum_value_transformation(self):
        """Test enum value transformation."""
        transformer = IDLTransformer()
        
        name_token = Token('IDENTIFIER', 'SUCCESS')
        value = LiteralExpression(value=0)
        
        result = transformer.enum_value([name_token, value])
        
        assert isinstance(result, EnumValue)
        assert result.name == "SUCCESS"
        assert result.value.value == 0