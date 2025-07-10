"""Additional generator tests for better coverage."""

import pytest
from pathlib import Path

from minimidl.ast.nodes import (
    ArrayType, Constant, ConstantValue, DictType, Enum, EnumValue,
    ForwardDeclaration, IDLFile, Interface, LiteralExpression, Method,
    Namespace, NullableType, Parameter, PrimitiveType, Property, SetType,
    Typedef, TypeRef
)
from minimidl.generators.cpp import CppGenerator
from minimidl.generators.c_wrapper import CWrapperGenerator
from minimidl.generators.swift import SwiftGenerator


class TestCppGeneratorCoverage:
    """Additional C++ generator tests."""

    def test_cpp_type_mapping(self):
        """Test C++ type conversions."""
        gen = CppGenerator()
        
        # Primitive types
        assert gen.cpp_type(PrimitiveType(name="void")) == "void"
        assert gen.cpp_type(PrimitiveType(name="bool")) == "bool"
        assert gen.cpp_type(PrimitiveType(name="int32_t")) == "int32_t"
        assert gen.cpp_type(PrimitiveType(name="int64_t")) == "int64_t"
        assert gen.cpp_type(PrimitiveType(name="float")) == "float"
        assert gen.cpp_type(PrimitiveType(name="double")) == "double"
        assert gen.cpp_type(PrimitiveType(name="string_t")) == "std::string"
        
        # Type reference
        assert gen.cpp_type(TypeRef(name="IUser")) == "std::shared_ptr<IUser>"
        
        # Array type
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert gen.cpp_type(array_type) == "std::vector<int32_t>"
        
        # Dict type
        dict_type = DictType(
            key_type=PrimitiveType(name="string_t"),
            value_type=PrimitiveType(name="int32_t")
        )
        assert gen.cpp_type(dict_type) == "std::unordered_map<std::string, int32_t>"
        
        # Set type
        set_type = SetType(element_type=PrimitiveType(name="string_t"))
        assert gen.cpp_type(set_type) == "std::unordered_set<std::string>"
        
        # Nullable type
        nullable = NullableType(inner_type=PrimitiveType(name="string_t"))
        assert gen.cpp_type(nullable) == "std::optional<std::string>"

    def test_generate_header_with_all_features(self, tmp_path):
        """Test header generation with all features."""
        gen = CppGenerator()
        
        # Create complex AST
        ast = IDLFile(namespaces=[
            Namespace(
                name="TestAPI",
                interfaces=[
                    Interface(
                        name="IUser",
                        methods=[
                            Method(
                                name="GetId",
                                return_type=PrimitiveType(name="int32_t"),
                                parameters=[]
                            ),
                            Method(
                                name="SetName",
                                return_type=PrimitiveType(name="void"),
                                parameters=[
                                    Parameter(
                                        name="name",
                                        type=PrimitiveType(name="string_t")
                                    )
                                ]
                            )
                        ],
                        properties=[
                            Property(
                                name="email",
                                type=PrimitiveType(name="string_t"),
                                writable=True
                            ),
                            Property(
                                name="active",
                                type=PrimitiveType(name="bool"),
                                writable=False
                            )
                        ]
                    )
                ],
                enums=[
                    Enum(
                        name="Status",
                        backing_type="int32_t",
                        values=[
                            EnumValue(name="ACTIVE", value=LiteralExpression(value=0)),
                            EnumValue(name="INACTIVE", value=LiteralExpression(value=1))
                        ]
                    )
                ],
                typedefs=[
                    Typedef(
                        name="UserId",
                        type=PrimitiveType(name="int32_t")
                    )
                ],
                constants=[
                    Constant(
                        name="MAX_USERS",
                        constant_value=ConstantValue(
                            type="int32_t",
                            value=LiteralExpression(value=100)
                        )
                    )
                ],
                forward_declarations=[
                    ForwardDeclaration(name="IManager")
                ]
            )
        ])
        
        output_dir = tmp_path / "cpp"
        gen.generate(ast, output_dir)
        
        # Check generated files
        header = output_dir / "include" / "testapi.hpp"
        assert header.exists()
        
        content = header.read_text()
        assert "namespace TestAPI" in content
        assert "class IUser" in content
        assert "enum class Status : int32_t" in content
        assert "using UserId = int32_t" in content
        assert "constexpr int32_t MAX_USERS = 100" in content
        assert "class IManager;" in content


class TestCWrapperGeneratorCoverage:
    """Additional C wrapper generator tests."""

    def test_c_type_mapping(self):
        """Test C type conversions."""
        gen = CWrapperGenerator()
        
        # Primitive types
        assert gen.c_type(PrimitiveType(name="void")) == "void"
        assert gen.c_type(PrimitiveType(name="bool")) == "bool"
        assert gen.c_type(PrimitiveType(name="int32_t")) == "int32_t"
        assert gen.c_type(PrimitiveType(name="int64_t")) == "int64_t"
        assert gen.c_type(PrimitiveType(name="float")) == "float"
        assert gen.c_type(PrimitiveType(name="double")) == "double"
        assert gen.c_type(PrimitiveType(name="string_t")) == "const char*"
        
        # Type reference
        assert gen.c_type(TypeRef(name="IUser")) == "TestAPI_IUser_t"
        
        # Array type - returns opaque handle
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert "handle" in gen.c_type(array_type).lower()

    def test_handle_name_generation(self):
        """Test handle name generation."""
        gen = CWrapperGenerator()
        gen.namespace_name = "TestAPI"
        
        assert gen.handle_name("IUser") == "TestAPI_IUser_t"
        assert gen.handle_name("Status") == "TestAPI_Status_t"

    def test_function_name_generation(self):
        """Test function name generation."""
        gen = CWrapperGenerator()
        gen.namespace_name = "TestAPI"
        
        assert gen.function_name("IUser", "GetName") == "TestAPI_IUser_GetName"
        assert gen.function_name("IManager", "Create") == "TestAPI_IManager_Create"

    def test_generate_wrapper_with_properties(self, tmp_path):
        """Test wrapper generation with properties."""
        gen = CWrapperGenerator()
        
        ast = IDLFile(namespaces=[
            Namespace(
                name="Test",
                interfaces=[
                    Interface(
                        name="IConfig",
                        methods=[],
                        properties=[
                            Property(
                                name="version",
                                type=PrimitiveType(name="string_t"),
                                writable=False
                            ),
                            Property(
                                name="debug",
                                type=PrimitiveType(name="bool"),
                                writable=True
                            )
                        ]
                    )
                ]
            )
        ])
        
        output_dir = tmp_path / "wrapper"
        gen.generate(ast, output_dir)
        
        header = output_dir / "include" / "test_wrapper.h"
        assert header.exists()
        
        content = header.read_text()
        # Read-only property has only getter
        assert "Test_IConfig_GetVersion" in content
        assert "Test_IConfig_SetVersion" not in content
        
        # Writable property has both getter and setter
        assert "Test_IConfig_GetDebug" in content
        assert "Test_IConfig_SetDebug" in content


class TestSwiftGeneratorCoverage:
    """Additional Swift generator tests."""

    def test_swift_type_mapping(self):
        """Test Swift type conversions."""
        gen = SwiftGenerator()
        
        # Primitive types
        assert gen.swift_type(PrimitiveType(name="void")) == "Void"
        assert gen.swift_type(PrimitiveType(name="bool")) == "Bool"
        assert gen.swift_type(PrimitiveType(name="int32_t")) == "Int32"
        assert gen.swift_type(PrimitiveType(name="int64_t")) == "Int64"
        assert gen.swift_type(PrimitiveType(name="float")) == "Float"
        assert gen.swift_type(PrimitiveType(name="double")) == "Double"
        assert gen.swift_type(PrimitiveType(name="string_t")) == "String"
        
        # Type reference
        assert gen.swift_type(TypeRef(name="IUser")) == "IUser"
        
        # Array type
        array_type = ArrayType(element_type=PrimitiveType(name="int32_t"))
        assert gen.swift_type(array_type) == "[Int32]"
        
        # Dict type
        dict_type = DictType(
            key_type=PrimitiveType(name="string_t"),
            value_type=PrimitiveType(name="int32_t")
        )
        assert gen.swift_type(dict_type) == "[String: Int32]"
        
        # Set type
        set_type = SetType(element_type=PrimitiveType(name="string_t"))
        assert gen.swift_type(set_type) == "Set<String>"
        
        # Nullable type
        nullable = NullableType(inner_type=PrimitiveType(name="string_t"))
        assert gen.swift_type(nullable) == "String?"
        
        # String type for enum backing
        assert gen.swift_type("int32_t") == "Int32"

    def test_swift_name_conversion(self):
        """Test Swift name conventions."""
        gen = SwiftGenerator()
        
        assert gen.swift_name("GetUserName") == "getUserName"
        assert gen.swift_name("ID") == "id"
        assert gen.swift_name("XMLParser") == "xmlParser"
        assert gen.swift_name("parseJSON") == "parseJSON"  # Already lowercase

    def test_generate_swift_with_enums(self, tmp_path):
        """Test Swift generation with enums."""
        gen = SwiftGenerator()
        
        ast = IDLFile(namespaces=[
            Namespace(
                name="Test",
                interfaces=[],
                enums=[
                    Enum(
                        name="Color",
                        backing_type="int32_t",
                        values=[
                            EnumValue(name="RED", value=LiteralExpression(value=0)),
                            EnumValue(name="GREEN", value=LiteralExpression(value=1)),
                            EnumValue(name="BLUE", value=LiteralExpression(value=2))
                        ]
                    )
                ]
            )
        ])
        
        output_dir = tmp_path / "swift"
        gen.generate(ast, output_dir)
        
        swift_file = output_dir / "Sources" / "Test" / "Test.swift"
        assert swift_file.exists()
        
        content = swift_file.read_text()
        assert "enum Color: Int32" in content
        assert "case red = 0" in content
        assert "case green = 1" in content
        assert "case blue = 2" in content

    def test_generate_package_swift(self, tmp_path):
        """Test Package.swift generation."""
        gen = SwiftGenerator()
        
        ast = IDLFile(namespaces=[
            Namespace(name="TestLib", interfaces=[])
        ])
        
        output_dir = tmp_path / "swift"
        gen.generate(ast, output_dir)
        
        package = output_dir / "Package.swift"
        assert package.exists()
        
        content = package.read_text()
        assert 'name: "TestLib"' in content
        assert ".target(" in content
        assert "swift-tools-version:" in content