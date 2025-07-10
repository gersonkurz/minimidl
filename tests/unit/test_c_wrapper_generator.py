"""Tests for C wrapper code generator."""

from pathlib import Path

import pytest

from minimidl.ast.nodes import (
    ArrayType,
    DictType,
    Enum,
    EnumValue,
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
    TypeRef,
)
from minimidl.generators.c_wrapper import CWrapperGenerator


class TestCWrapperTypeMapping:
    """Test C wrapper type mapping."""

    @pytest.fixture
    def generator(self):
        """Create a C wrapper generator instance."""
        return CWrapperGenerator()

    def test_primitive_types(self, generator):
        """Test primitive type mapping."""
        assert generator.c_type(PrimitiveType(name="void")) == "void"
        assert generator.c_type(PrimitiveType(name="bool")) == "bool"
        assert generator.c_type(PrimitiveType(name="int32_t")) == "int32_t"
        assert generator.c_type(PrimitiveType(name="int64_t")) == "int64_t"
        assert generator.c_type(PrimitiveType(name="float")) == "float"
        assert generator.c_type(PrimitiveType(name="double")) == "double"
        assert generator.c_type(PrimitiveType(name="string_t")) == "const char*"

    def test_interface_types(self, generator):
        """Test interface type mapping to handles."""
        type_ref = TypeRef(name="ILogger")
        assert generator.c_type(type_ref) == "ILogger_Handle"

    def test_collection_types(self, generator):
        """Test collection type mapping."""
        generator.namespace_prefix = "Test"

        # Arrays become handles
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert generator.c_type(array_type) == "TestArray_Handle"

        # Dicts become handles
        dict_type = DictType(
            key_type=PrimitiveType(name="string_t"),
            value_type=PrimitiveType(name="int32_t"),
        )
        assert generator.c_type(dict_type) == "TestDict_Handle"

        # Sets become handles
        set_type = SetType(element_type=PrimitiveType(name="string_t"))
        assert generator.c_type(set_type) == "TestSet_Handle"

    def test_nullable_types(self, generator):
        """Test nullable type mapping."""
        # Nullable types map to same as non-nullable in C
        nullable_int = NullableType(inner_type=PrimitiveType(name="int32_t"))
        assert generator.c_type(nullable_int) == "int32_t"

        nullable_ref = NullableType(inner_type=TypeRef(name="ILogger"))
        assert generator.c_type(nullable_ref) == "ILogger_Handle"

    def test_function_names(self, generator):
        """Test C function name generation."""
        assert generator.c_function_name("ILogger", "name", "Get") == "ILogger_Getname"
        assert generator.c_function_name("ILogger", "name", "Set") == "ILogger_Setname"
        assert generator.c_function_name("ILogger", "log") == "ILogger_log"

    def test_type_predicates(self, generator):
        """Test type predicate functions."""
        # Primitive types
        assert generator.is_primitive(PrimitiveType(name="int32_t")) == True
        assert generator.is_primitive(PrimitiveType(name="string_t")) == False

        # String type
        assert generator.is_string(PrimitiveType(name="string_t")) == True
        assert generator.is_string(PrimitiveType(name="int32_t")) == False

        # Collection types
        assert (
            generator.is_array(ArrayType(element_type=PrimitiveType(name="int32_t")))
            == True
        )
        assert (
            generator.is_dict(
                DictType(
                    key_type=PrimitiveType(name="string_t"),
                    value_type=PrimitiveType(name="int32_t"),
                )
            )
            == True
        )
        assert (
            generator.is_set(SetType(element_type=PrimitiveType(name="string_t")))
            == True
        )

        # Interface types
        assert generator.is_interface(TypeRef(name="ILogger")) == True

        # Nullable types - should look through
        assert (
            generator.is_primitive(
                NullableType(inner_type=PrimitiveType(name="int32_t"))
            )
            == True
        )
        assert (
            generator.is_string(NullableType(inner_type=PrimitiveType(name="string_t")))
            == True
        )


class TestCWrapperGeneration:
    """Test full C wrapper code generation."""

    @pytest.fixture
    def generator(self):
        """Create a C wrapper generator instance."""
        return CWrapperGenerator()

    def test_simple_interface(self, generator, tmp_path):
        """Test generating a simple C wrapper."""
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
                    properties=[
                        Property(
                            name="value",
                            type=PrimitiveType(name="int32_t"),
                            writable=True,
                        )
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

        # Should generate 5 files
        assert len(generated) == 5

        # Check header file
        header_file = tmp_path / "example_wrapper.h"
        assert header_file.exists()
        content = header_file.read_text()

        # Check for handle typedef
        assert "typedef void* ISimple_Handle;" in content

        # Check for create/release functions
        assert "ISimple_Handle ISimple_Create();" in content
        assert "void ISimple_Release(ISimple_Handle handle);" in content

        # Check for property accessors
        assert "int32_t ISimple_Getvalue(ISimple_Handle handle);" in content
        assert "void ISimple_Setvalue(ISimple_Handle handle, int32_t value);" in content

        # Check for method
        assert "void ISimple_doSomething(" in content
        assert "ISimple_Handle handle)" in content

        # Check implementation file
        impl_file = tmp_path / "example_wrapper.cpp"
        assert impl_file.exists()

        # Check exports file
        exports_file = tmp_path / "example_exports.def"
        assert exports_file.exists()
        exports_content = exports_file.read_text()
        assert "ISimple_Create" in exports_content
        assert "ISimple_Getvalue" in exports_content

        # Check CMakeLists.txt
        cmake_file = tmp_path / "CMakeLists.txt"
        assert cmake_file.exists()

        # Check test file
        test_file = tmp_path / "example_test.c"
        assert test_file.exists()

    def test_enum_generation(self, generator, tmp_path):
        """Test enum generation in C wrapper."""
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

        header_file = tmp_path / "example_wrapper.h"
        content = header_file.read_text()

        # Check enum typedef and values
        assert "typedef int32_t Status;" in content
        assert "#define Status_OK 0" in content
        assert "#define Status_ERROR 1" in content

    def test_array_property(self, generator, tmp_path):
        """Test array property handling."""
        namespace = Namespace(
            name="Example",
            interfaces=[
                Interface(
                    name="IContainer",
                    methods=[],
                    properties=[
                        Property(
                            name="items",
                            type=ArrayType(element_type=PrimitiveType(name="string_t")),
                            writable=True,
                        )
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

        header_file = tmp_path / "example_wrapper.h"
        content = header_file.read_text()

        # Check array access functions
        assert "size_t IContainer_Getitems_Count(IContainer_Handle handle);" in content
        assert (
            "const char* IContainer_Getitems_Item(IContainer_Handle handle, size_t index);"
            in content
        )
        assert "void IContainer_Setitems_Clear(IContainer_Handle handle);" in content
        assert (
            "void IContainer_Setitems_Add(IContainer_Handle handle, const char* value);"
            in content
        )

    def test_error_handling(self, generator, tmp_path):
        """Test error handling functions."""
        namespace = Namespace(
            name="Example",
            interfaces=[],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        header_file = tmp_path / "example_wrapper.h"
        content = header_file.read_text()

        # Check error handling functions
        assert "const char* Example_GetLastError();" in content
        assert "void Example_ClearError();" in content

        # Check error codes enum
        assert "typedef enum {" in content
        assert "EXAMPLE_OK = 0," in content
        assert "EXAMPLE_ERROR_NULL_POINTER = -1," in content

    def test_export_macros(self, generator, tmp_path):
        """Test platform-specific export macros."""
        namespace = Namespace(
            name="Example",
            interfaces=[],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        header_file = tmp_path / "example_wrapper.h"
        content = header_file.read_text()

        # Check export macro definition
        assert "#ifdef _WIN32" in content
        assert "__declspec(dllexport)" in content
        assert "__declspec(dllimport)" in content
        assert '__attribute__((visibility("default")))' in content
        assert "EXAMPLE_API" in content
