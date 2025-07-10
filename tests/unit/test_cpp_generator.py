"""Tests for C++ code generator."""

from pathlib import Path

import pytest

from minimidl.ast.nodes import (
    ArrayType,
    BinaryExpression,
    Constant,
    ConstantValue,
    DictType,
    Enum,
    EnumValue,
    ForwardDeclaration,
    IdentifierExpression,
    IDLFile,
    Interface,
    LiteralExpression,
    Method,
    Namespace,
    NullableType,
    Parameter,
    PrimitiveType,
    Property,
    SetType,
    Typedef,
    TypeRef,
)
from minimidl.generators.cpp import CppGenerator


class TestCppTypeMapping:
    """Test C++ type mapping."""

    @pytest.fixture
    def generator(self):
        """Create a C++ generator instance."""
        return CppGenerator()

    def test_primitive_types(self, generator):
        """Test primitive type mapping."""
        assert generator.cpp_type(PrimitiveType(name="void")) == "void"
        assert generator.cpp_type(PrimitiveType(name="bool")) == "bool"
        assert generator.cpp_type(PrimitiveType(name="int32_t")) == "int32_t"
        assert generator.cpp_type(PrimitiveType(name="int64_t")) == "int64_t"
        assert generator.cpp_type(PrimitiveType(name="float")) == "float"
        assert generator.cpp_type(PrimitiveType(name="double")) == "double"
        assert generator.cpp_type(PrimitiveType(name="string_t")) == "std::string"

    def test_array_type(self, generator):
        """Test array type mapping."""
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert generator.cpp_type(array_type) == "std::vector<int32_t>"

        # Nested array
        nested = ArrayType(
            element_type=ArrayType(element_type=PrimitiveType(name="bool"))
        )
        assert generator.cpp_type(nested) == "std::vector<std::vector<bool>>"

    def test_dict_type(self, generator):
        """Test dictionary type mapping."""
        dict_type = DictType(
            key_type=PrimitiveType(name="string_t"),
            value_type=PrimitiveType(name="int32_t"),
        )
        assert (
            generator.cpp_type(dict_type) == "std::unordered_map<std::string, int32_t>"
        )

    def test_set_type(self, generator):
        """Test set type mapping."""
        set_type = SetType(element_type=PrimitiveType(name="string_t"))
        assert generator.cpp_type(set_type) == "std::unordered_set<std::string>"

    def test_nullable_types(self, generator):
        """Test nullable type mapping."""
        # Nullable primitive uses optional
        nullable_int = NullableType(inner_type=PrimitiveType(name="int32_t"))
        assert generator.cpp_type(nullable_int) == "std::optional<int32_t>"

        # Nullable object uses shared_ptr
        nullable_ref = NullableType(inner_type=TypeRef(name="IFoo"))
        assert generator.cpp_type(nullable_ref) == "std::shared_ptr<IFoo>"

    def test_type_refs(self, generator):
        """Test type reference mapping."""
        type_ref = TypeRef(name="MyEnum")
        assert generator.cpp_type(type_ref) == "MyEnum"

    def test_param_types(self, generator):
        """Test parameter type mapping."""
        # Primitives by value
        assert generator.cpp_param_type(PrimitiveType(name="int32_t")) == "int32_t"
        assert generator.cpp_param_type(PrimitiveType(name="bool")) == "bool"

        # String by const ref
        assert (
            generator.cpp_param_type(PrimitiveType(name="string_t"))
            == "const std::string&"
        )

        # Complex types by const ref
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert generator.cpp_param_type(array_type) == "const std::vector<int32_t>&"


class TestExpressionRendering:
    """Test expression rendering to C++."""

    @pytest.fixture
    def generator(self):
        """Create a C++ generator instance."""
        return CppGenerator()

    def test_literal_expressions(self, generator):
        """Test literal expression rendering."""
        # Decimal
        expr = LiteralExpression(value=42)
        assert generator.render_expression(expr) == "42"

        # Hex
        expr = LiteralExpression(value=255, base="hex")
        assert generator.render_expression(expr) == "0xFF"

        # Binary
        expr = LiteralExpression(value=5, base="binary")
        assert generator.render_expression(expr) == "0b101"

    def test_identifier_expressions(self, generator):
        """Test identifier expression rendering."""
        expr = IdentifierExpression(name="MY_CONSTANT")
        assert generator.render_expression(expr) == "MY_CONSTANT"

    def test_binary_expressions(self, generator):
        """Test binary expression rendering."""
        left = LiteralExpression(value=1)
        right = LiteralExpression(value=2)
        expr = BinaryExpression(operator="<<", left=left, right=right)
        assert generator.render_expression(expr) == "(1 << 2)"

    def test_complex_expressions(self, generator):
        """Test complex expression rendering."""
        # (1 << 4) | 0xFF
        shift = BinaryExpression(
            operator="<<",
            left=LiteralExpression(value=1),
            right=LiteralExpression(value=4),
        )
        expr = BinaryExpression(
            operator="|", left=shift, right=LiteralExpression(value=255, base="hex")
        )
        assert generator.render_expression(expr) == "((1 << 4) | 0xFF)"


class TestCodeGeneration:
    """Test full code generation."""

    @pytest.fixture
    def generator(self):
        """Create a C++ generator instance."""
        return CppGenerator()

    def test_simple_interface(self, generator, tmp_path):
        """Test generating a simple interface."""
        # Create AST
        namespace = Namespace(
            name="Example",
            interfaces=[
                Interface(
                    name="ISimple",
                    methods=[
                        Method(
                            name="doSomething",
                            return_type=PrimitiveType(name="void"),
                            parameters=[],
                        )
                    ],
                    properties=[],
                )
            ],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])

        # Generate code
        generated = generator.generate(idl_file, tmp_path)

        # Check generated file
        assert len(generated) == 1
        assert generated[0].name == "example.hpp"

        content = generated[0].read_text()
        assert "namespace Example" in content
        assert "class ISimple" in content
        assert "virtual void doSomething() = 0;" in content

    def test_enum_generation(self, generator, tmp_path):
        """Test enum generation."""
        namespace = Namespace(
            name="Example",
            interfaces=[],
            enums=[
                Enum(
                    name="Status",
                    backing_type="int32_t",
                    values=[
                        EnumValue(name="OK", value=LiteralExpression(value=0)),
                        EnumValue(name="ERROR", value=LiteralExpression(value=1)),
                    ],
                )
            ],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        content = generated[0].read_text()
        assert "enum class Status : int32_t" in content
        assert "OK = 0," in content
        assert "ERROR = 1," in content

    def test_property_generation(self, generator, tmp_path):
        """Test property generation."""
        namespace = Namespace(
            name="Example",
            interfaces=[
                Interface(
                    name="IConfig",
                    methods=[],
                    properties=[
                        Property(
                            name="name",
                            type=PrimitiveType(name="string_t"),
                            writable=False,
                        ),
                        Property(
                            name="value",
                            type=PrimitiveType(name="int32_t"),
                            writable=True,
                        ),
                    ],
                )
            ],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        content = generated[0].read_text()
        # Read-only property
        assert "virtual std::string get_name() const = 0;" in content
        assert "set_name" not in content

        # Writable property
        assert "virtual int32_t get_value() const = 0;" in content
        assert "virtual void set_value(int32_t value) = 0;" in content

    def test_complex_types(self, generator, tmp_path):
        """Test complex type generation."""
        namespace = Namespace(
            name="Example",
            interfaces=[
                Interface(
                    name="IContainer",
                    methods=[
                        Method(
                            name="processData",
                            return_type=ArrayType(
                                element_type=PrimitiveType(name="int32_t")
                            ),
                            parameters=[
                                Parameter(
                                    name="input",
                                    type=DictType(
                                        key_type=PrimitiveType(name="string_t"),
                                        value_type=NullableType(
                                            inner_type=TypeRef(name="IProcessor")
                                        ),
                                    ),
                                )
                            ],
                        )
                    ],
                    properties=[],
                )
            ],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        content = generated[0].read_text()
        expected = "virtual std::vector<int32_t> processData(const std::unordered_map<std::string, std::shared_ptr<IProcessor>>& input) = 0;"
        assert expected in content
