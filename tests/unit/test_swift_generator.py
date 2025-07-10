"""Tests for Swift code generator."""

from pathlib import Path

import pytest

from minimidl.ast.nodes import (
    ArrayType,
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
    TypeRef,
)
from minimidl.generators.swift import SwiftGenerator


class TestSwiftTypeMapping:
    """Test Swift type mapping."""

    @pytest.fixture
    def generator(self):
        """Create a Swift generator instance."""
        return SwiftGenerator()

    def test_primitive_types(self, generator):
        """Test primitive type mapping."""
        assert generator.swift_type(PrimitiveType(name="void")) == "Void"
        assert generator.swift_type(PrimitiveType(name="bool")) == "Bool"
        assert generator.swift_type(PrimitiveType(name="int32_t")) == "Int32"
        assert generator.swift_type(PrimitiveType(name="int64_t")) == "Int64"
        assert generator.swift_type(PrimitiveType(name="float")) == "Float"
        assert generator.swift_type(PrimitiveType(name="double")) == "Double"
        assert generator.swift_type(PrimitiveType(name="string_t")) == "String"

    def test_array_types(self, generator):
        """Test array type mapping."""
        # Simple array
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert generator.swift_type(array_type) == "[Int32]"

        # String array
        string_array = ArrayType(element_type=PrimitiveType(name="string_t"))
        assert generator.swift_type(string_array) == "[String]"

        # Nested array
        nested = ArrayType(
            element_type=ArrayType(element_type=PrimitiveType(name="bool"))
        )
        assert generator.swift_type(nested) == "[[Bool]]"

    def test_nullable_types(self, generator):
        """Test nullable type mapping."""
        # Nullable primitive
        nullable_int = NullableType(inner_type=PrimitiveType(name="int32_t"))
        assert generator.swift_type(nullable_int) == "Int32?"

        # Nullable string
        nullable_string = NullableType(inner_type=PrimitiveType(name="string_t"))
        assert generator.swift_type(nullable_string) == "String?"

        # Nullable interface
        nullable_ref = NullableType(inner_type=TypeRef(name="IUser"))
        assert generator.swift_type(nullable_ref) == "User?"

    def test_class_name_conversion(self, generator):
        """Test interface name to Swift class name conversion."""
        assert generator.swift_class_name("IUser") == "User"
        assert generator.swift_class_name("IEventHandler") == "EventHandler"
        assert generator.swift_class_name("User") == "User"  # No I prefix
        assert generator.swift_class_name("I") == "I"  # Edge case

    def test_type_predicates(self, generator):
        """Test type predicate functions."""
        # String checks
        assert generator.is_string(PrimitiveType(name="string_t")) == True
        assert generator.is_string(PrimitiveType(name="int32_t")) == False
        assert (
            generator.is_string(NullableType(inner_type=PrimitiveType(name="string_t")))
            == True
        )

        # Primitive checks
        assert generator.is_primitive(PrimitiveType(name="int32_t")) == True
        assert generator.is_primitive(PrimitiveType(name="string_t")) == False

        # Array checks
        assert (
            generator.is_array(ArrayType(element_type=PrimitiveType(name="int32_t")))
            == True
        )
        assert generator.is_array(PrimitiveType(name="int32_t")) == False


class TestSwiftGeneration:
    """Test Swift code generation."""

    @pytest.fixture
    def generator(self):
        """Create a Swift generator instance."""
        return SwiftGenerator()

    def test_simple_interface(self, generator, tmp_path):
        """Test generating a simple Swift package."""
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

        # Check generated files
        assert (
            len(generated) == 6
        )  # Package.swift, Types, wrapper, modulemap, README, tests

        # Check Package.swift
        package_file = tmp_path / "Example" / "Package.swift"
        assert package_file.exists()
        content = package_file.read_text()
        assert 'name: "Example"' in content
        assert '.library(\n            name: "Example"' in content
        assert '.systemLibrary(\n            name: "ExampleC"' in content

        # Check Swift wrapper
        wrapper_file = tmp_path / "Example" / "Sources" / "Example" / "Example.swift"
        assert wrapper_file.exists()
        content = wrapper_file.read_text()
        assert "public class Simple {" in content
        assert "internal let handle: OpaquePointer" in content
        assert "public var value: Int32" in content
        assert "public func doSomething()" in content

        # Check module map
        modulemap_file = (
            tmp_path / "Example" / "Sources" / "ExampleC" / "module.modulemap"
        )
        assert modulemap_file.exists()
        content = modulemap_file.read_text()
        assert "module ExampleC {" in content
        assert 'header "example_wrapper.h"' in content

    def test_enum_generation(self, generator, tmp_path):
        """Test enum generation in Swift."""
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

        types_file = tmp_path / "Example" / "Sources" / "Example" / "Types.swift"
        content = types_file.read_text()

        # Check enum definition
        assert "public enum Status: Int32, CaseIterable {" in content
        assert "case ok = 0" in content
        assert "case error = 1" in content
        assert "public init?(cValue: Example_Status)" in content
        assert "public var cValue: Example_Status" in content

    def test_array_property(self, generator, tmp_path):
        """Test array property generation."""
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

        wrapper_file = tmp_path / "Example" / "Sources" / "Example" / "Example.swift"
        content = wrapper_file.read_text()

        # Check array property
        assert "public var items: [String]" in content
        assert "IContainer_Getitems_Count(handle)" in content
        assert "IContainer_Getitems_Item(handle, i)" in content
        assert "String(cString: cString)" in content
        assert "IContainer_Setitems_Clear(handle)" in content
        assert "IContainer_Setitems_Add(handle, item)" in content

    def test_nullable_property(self, generator, tmp_path):
        """Test nullable property generation."""
        namespace = Namespace(
            name="Example",
            interfaces=[
                Interface(
                    name="IApplication",
                    methods=[],
                    properties=[
                        Property(
                            name="user",
                            type=NullableType(inner_type=TypeRef(name="IUser")),
                            writable=True,
                        )
                    ],
                ),
                Interface(name="IUser", methods=[], properties=[]),
            ],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        wrapper_file = tmp_path / "Example" / "Sources" / "Example" / "Example.swift"
        content = wrapper_file.read_text()

        # Check nullable interface property
        assert "public var user: User?" in content
        assert "return nil" in content
        assert "newValue?.handle" in content

    def test_method_with_parameters(self, generator, tmp_path):
        """Test method with parameters generation."""
        namespace = Namespace(
            name="Example",
            interfaces=[
                Interface(
                    name="ILogger",
                    methods=[
                        Method(
                            name="log",
                            return_type=PrimitiveType(name="void"),
                            parameters=[
                                Parameter(name="level", type=TypeRef(name="LogLevel")),
                                Parameter(
                                    name="message", type=PrimitiveType(name="string_t")
                                ),
                            ],
                        )
                    ],
                    properties=[],
                )
            ],
            enums=[
                Enum(
                    name="LogLevel",
                    backing_type="int32_t",
                    values=[EnumValue(name="INFO", value=LiteralExpression(value=0))],
                )
            ],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generator.enum_names = {"LogLevel"}  # Set enum names for type resolution
        generated = generator.generate(idl_file, tmp_path)

        wrapper_file = tmp_path / "Example" / "Sources" / "Example" / "Example.swift"
        content = wrapper_file.read_text()

        # Check method signature
        assert "public func log(level: LogLevel, message: String)" in content
        assert "ILogger_log(" in content
        assert "handle, level.cValue, message)" in content

    def test_test_generation(self, generator, tmp_path):
        """Test unit test file generation."""
        namespace = Namespace(
            name="Example",
            interfaces=[Interface(name="ISimple", methods=[], properties=[])],
            enums=[],
            typedefs=[],
            constants=[],
            forward_declarations=[],
        )

        idl_file = IDLFile(namespaces=[namespace])
        generated = generator.generate(idl_file, tmp_path)

        test_file = (
            tmp_path / "Example" / "Tests" / "ExampleTests" / "ExampleTests.swift"
        )
        assert test_file.exists()
        content = test_file.read_text()

        # Check test structure
        assert "import XCTest" in content
        assert "@testable import Example" in content
        assert "final class ExampleTests: XCTestCase" in content
        assert "func testSimpleCreation()" in content
