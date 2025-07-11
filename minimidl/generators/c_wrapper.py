"""C wrapper generator for MinimIDL."""

from pathlib import Path
from typing import Any

from minimidl.ast.nodes import (
    ArrayType,
    BinaryExpression,
    DictType,
    Enum,
    Expression,
    IdentifierExpression,
    IDLFile,
    Interface,
    LiteralExpression,
    Method,
    Namespace,
    NullableType,
    Parameter,
    ParenthesizedExpression,
    PrimitiveType,
    Property,
    SetType,
    Type,
    TypeRef,
    UnaryExpression,
)
from minimidl.generators.base import BaseGenerator


class CWrapperGenerator(BaseGenerator):
    """Generate C wrapper code from MinimIDL AST."""

    def __init__(self, template_dir: Path | None = None) -> None:
        """Initialize the C wrapper generator."""
        super().__init__(template_dir)
        self.namespace_prefix = ""
        self.enum_names: set[str] = set()

    def get_custom_filters(self) -> dict[str, Any]:
        """Get C wrapper specific Jinja2 filters."""
        return {
            "c_type": self.c_type,
            "c_param_type": self.c_param_type,
            "c_return_type": self.c_return_type,
            "c_handle_type": self.c_handle_type,
            "c_function_name": self.c_function_name,
            "needs_array_interface": self.needs_array_interface,
            "needs_dict_interface": self.needs_dict_interface,
            "needs_set_interface": self.needs_set_interface,
            "is_nullable": self.is_nullable,
            "is_primitive": self.is_primitive,
            "is_string": self.is_string,
            "is_array": self.is_array,
            "is_dict": self.is_dict,
            "is_set": self.is_set,
            "is_enum": self.is_enum,
            "is_interface": self.is_interface,
            "export_macro": self.export_macro,
            "render_expression": self.render_expression,
        }

    def c_type(self, type_spec: Type) -> str:
        """Convert IDL type to C type.

        Args:
            type_spec: IDL type specification

        Returns:
            C type string
        """
        if isinstance(type_spec, PrimitiveType):
            type_map = {
                "void": "void",
                "bool": "bool",
                "int32_t": "int32_t",
                "int64_t": "int64_t",
                "float": "float",
                "double": "double",
                "string_t": "const char*",
            }
            return type_map.get(type_spec.name, type_spec.name)

        elif isinstance(type_spec, TypeRef):
            # Check if it's an enum or interface
            if type_spec.name in self.enum_names:
                # Enums are just typedefs
                return type_spec.name
            else:
                # For interfaces, we use handles
                return f"{type_spec.name}_Handle"

        elif isinstance(type_spec, ArrayType):
            # Arrays need special handling - return handle
            return f"{self.namespace_prefix}Array_Handle"

        elif isinstance(type_spec, DictType):
            # Dicts need special handling - return handle
            return f"{self.namespace_prefix}Dict_Handle"

        elif isinstance(type_spec, SetType):
            # Sets need special handling - return handle
            return f"{self.namespace_prefix}Set_Handle"

        elif isinstance(type_spec, NullableType):
            # Nullable types are the same as non-nullable in C
            # NULL represents the null value
            return self.c_type(type_spec.inner_type)

        return "void*"

    def c_param_type(self, type_spec: Type) -> str:
        """Get C parameter type.

        Args:
            type_spec: IDL type specification

        Returns:
            C parameter type string
        """
        # Most types are the same for parameters
        return self.c_type(type_spec)

    def c_return_type(self, type_spec: Type) -> str:
        """Get C return type.

        Args:
            type_spec: IDL type specification

        Returns:
            C return type string
        """
        # Most types are the same for returns
        return self.c_type(type_spec)

    def c_handle_type(self, interface_name: str) -> str:
        """Get C handle type for an interface.

        Args:
            interface_name: Name of the interface

        Returns:
            C handle type name
        """
        return f"{interface_name}_Handle"

    def c_function_name(
        self, interface_name: str, member_name: str, prefix: str = ""
    ) -> str:
        """Generate C function name.

        Args:
            interface_name: Name of the interface
            member_name: Name of the method/property
            prefix: Optional prefix (Get/Set)

        Returns:
            C function name
        """
        if prefix:
            return f"{interface_name}_{prefix}{member_name}"
        return f"{interface_name}_{member_name}"

    def needs_array_interface(self, type_spec: Type) -> bool:
        """Check if type needs array iteration interface."""
        return isinstance(type_spec, ArrayType)

    def needs_dict_interface(self, type_spec: Type) -> bool:
        """Check if type needs dictionary iteration interface."""
        return isinstance(type_spec, DictType)

    def needs_set_interface(self, type_spec: Type) -> bool:
        """Check if type needs set iteration interface."""
        return isinstance(type_spec, SetType)

    def is_nullable(self, type_spec: Type) -> bool:
        """Check if type is nullable."""
        return isinstance(type_spec, NullableType)

    def is_primitive(self, type_spec: Type) -> bool:
        """Check if type is primitive."""
        if isinstance(type_spec, NullableType):
            return self.is_primitive(type_spec.inner_type)
        return isinstance(type_spec, PrimitiveType) and type_spec.name != "string_t"

    def is_string(self, type_spec: Type) -> bool:
        """Check if type is string."""
        if isinstance(type_spec, NullableType):
            return self.is_string(type_spec.inner_type)
        return isinstance(type_spec, PrimitiveType) and type_spec.name == "string_t"

    def is_array(self, type_spec: Type) -> bool:
        """Check if type is array."""
        if isinstance(type_spec, NullableType):
            return self.is_array(type_spec.inner_type)
        return isinstance(type_spec, ArrayType)

    def is_dict(self, type_spec: Type) -> bool:
        """Check if type is dictionary."""
        if isinstance(type_spec, NullableType):
            return self.is_dict(type_spec.inner_type)
        return isinstance(type_spec, DictType)

    def is_set(self, type_spec: Type) -> bool:
        """Check if type is set."""
        if isinstance(type_spec, NullableType):
            return self.is_set(type_spec.inner_type)
        return isinstance(type_spec, SetType)
    
    def is_enum(self, type_spec: Type) -> bool:
        """Check if type is an enum."""
        if isinstance(type_spec, NullableType):
            return self.is_enum(type_spec.inner_type)
        if isinstance(type_spec, TypeRef):
            # Check if this type name is in our enum names set
            return type_spec.name in self.enum_names
        return False

    def is_interface(self, type_spec: Type) -> bool:
        """Check if type is an interface reference."""
        if isinstance(type_spec, NullableType):
            return self.is_interface(type_spec.inner_type)
        return isinstance(type_spec, TypeRef)

    def export_macro(self, namespace: Namespace | str) -> str:
        """Get export macro name for namespace."""
        if isinstance(namespace, Namespace):
            return f"{namespace.name.upper()}_API"
        return f"{namespace.upper()}_API"

    def render_expression(self, expr: Expression) -> str:
        """Render an expression to C code.

        Args:
            expr: Expression AST node

        Returns:
            C expression string
        """
        if isinstance(expr, LiteralExpression):
            if expr.base == "hex":
                return f"0x{expr.value:X}"
            elif expr.base == "binary":
                # C doesn't support binary literals, convert to hex
                return f"0x{expr.value:X}"
            else:
                return str(expr.value)

        elif isinstance(expr, IdentifierExpression):
            return expr.name

        elif isinstance(expr, UnaryExpression):
            operand = self.render_expression(expr.operand)
            return f"{expr.operator}{operand}"

        elif isinstance(expr, BinaryExpression):
            left = self.render_expression(expr.left)
            right = self.render_expression(expr.right)
            return f"({left} {expr.operator} {right})"

        elif isinstance(expr, ParenthesizedExpression):
            inner = self.render_expression(expr.expression)
            return f"({inner})"

        # Fallback for direct values (from transformer)
        return str(expr)

    def generate(self, idl_file: IDLFile, output_dir: Path) -> list[Path]:
        """Generate C wrapper code from AST.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Directory to write generated files

        Returns:
            List of generated file paths
        """
        generated_files = []

        # For each namespace, generate wrapper files
        for namespace in idl_file.namespaces:
            self.namespace_prefix = namespace.name

            # Collect enum names for type resolution
            self.enum_names = {enum.name for enum in namespace.enums}

            # Generate wrapper header
            header_template = self.get_template("c_wrapper/wrapper.h.j2")
            header_content = header_template.render(namespace=namespace)
            header_path = self.write_file(
                output_dir, f"{namespace.name.lower()}_wrapper.h", header_content
            )
            generated_files.append(header_path)

            # Generate wrapper implementation
            impl_template = self.get_template("c_wrapper/wrapper.cpp.j2")
            impl_content = impl_template.render(namespace=namespace)
            impl_path = self.write_file(
                output_dir, f"{namespace.name.lower()}_wrapper.cpp", impl_content
            )
            generated_files.append(impl_path)

            # Generate Windows exports file
            exports_template = self.get_template("c_wrapper/exports.def.j2")
            exports_content = exports_template.render(namespace=namespace)
            exports_path = self.write_file(
                output_dir, f"{namespace.name.lower()}_exports.def", exports_content
            )
            generated_files.append(exports_path)

            # Generate CMakeLists.txt
            cmake_template = self.get_template("c_wrapper/CMakeLists.txt.j2")
            cmake_content = cmake_template.render(namespace=namespace)
            cmake_path = self.write_file(output_dir, "CMakeLists.txt", cmake_content)
            generated_files.append(cmake_path)

            # Generate test harness
            testbed_template = self.get_template("c_wrapper/testbed.c.j2")
            testbed_content = testbed_template.render(namespace=namespace)
            testbed_path = self.write_file(
                output_dir, f"{namespace.name.lower()}_test.c", testbed_content
            )
            generated_files.append(testbed_path)

        return generated_files

    def get_output_filename(self, namespace_name: str) -> str:
        """Get output filename for a namespace.

        Args:
            namespace_name: Name of the namespace

        Returns:
            Output filename
        """
        return f"{namespace_name.lower()}_wrapper"
