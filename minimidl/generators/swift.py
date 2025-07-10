"""Swift binding generator for MinimIDL."""

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
from minimidl.generators.c_wrapper import CWrapperGenerator


class SwiftGenerator(BaseGenerator):
    """Generate Swift bindings from MinimIDL AST."""

    def __init__(self, template_dir: Path | None = None) -> None:
        """Initialize the Swift generator."""
        super().__init__(template_dir)
        # We'll use the C wrapper generator for C function names
        self.c_gen = CWrapperGenerator()
        self.namespace_name = ""
        self.enum_names: set[str] = set()

    def get_custom_filters(self) -> dict[str, Any]:
        """Get Swift specific Jinja2 filters."""
        return {
            "swift_type": self.swift_type,
            "swift_param_type": self.swift_param_type,
            "swift_return_type": self.swift_return_type,
            "swift_class_name": self.swift_class_name,
            "c_function_name": self.c_gen.c_function_name,
            "is_nullable": self.is_nullable,
            "is_primitive": self.is_primitive,
            "is_string": self.is_string,
            "is_array": self.is_array,
            "is_dict": self.is_dict,
            "is_set": self.is_set,
            "is_interface": self.is_interface,
            "is_enum": self.is_enum,
            "needs_optional": self.needs_optional,
            "c_to_swift_value": self.c_to_swift_value,
            "swift_to_c_value": self.swift_to_c_value,
            "swift_to_c_param": lambda name, type_spec: self.swift_to_c_param(name, type_spec),
            "render_expression": self.render_expression,
            "capitalize": lambda s: s[0].upper() + s[1:] if s else "",
            "lower": lambda s: s.lower(),
        }

    def swift_type(self, type_spec: Type | str) -> str:
        """Convert IDL type to Swift type.

        Args:
            type_spec: IDL type specification or string type name

        Returns:
            Swift type string
        """
        # Handle string types (for enum backing types)
        if isinstance(type_spec, str):
            type_map = {
                "void": "Void",
                "bool": "Bool",
                "int32_t": "Int32",
                "int64_t": "Int64",
                "float": "Float",
                "double": "Double",
                "string_t": "String",
            }
            return type_map.get(type_spec, type_spec)
        
        if isinstance(type_spec, PrimitiveType):
            type_map = {
                "void": "Void",
                "bool": "Bool",
                "int32_t": "Int32",
                "int64_t": "Int64",
                "float": "Float",
                "double": "Double",
                "string_t": "String",
            }
            return type_map.get(type_spec.name, type_spec.name)

        elif isinstance(type_spec, TypeRef):
            # Could be enum or interface
            if type_spec.name in self.enum_names:
                return type_spec.name
            else:
                # Interface - use class name
                return self.swift_class_name(type_spec.name)

        elif isinstance(type_spec, ArrayType):
            element_type = self.swift_type(type_spec.element_type)
            return f"[{element_type}]"

        elif isinstance(type_spec, DictType):
            key_type = self.swift_type(type_spec.key_type)
            value_type = self.swift_type(type_spec.value_type)
            return f"[{key_type}: {value_type}]"

        elif isinstance(type_spec, SetType):
            element_type = self.swift_type(type_spec.element_type)
            return f"Set<{element_type}>"

        elif isinstance(type_spec, NullableType):
            inner_type = self.swift_type(type_spec.inner_type)
            return f"{inner_type}?"

        return "Any"

    def swift_param_type(self, type_spec: Type) -> str:
        """Get Swift parameter type.

        Args:
            type_spec: IDL type specification

        Returns:
            Swift parameter type string
        """
        # Most types are the same for parameters
        return self.swift_type(type_spec)

    def swift_return_type(self, type_spec: Type) -> str:
        """Get Swift return type.

        Args:
            type_spec: IDL type specification

        Returns:
            Swift return type string
        """
        # Most types are the same for returns
        return self.swift_type(type_spec)

    def swift_class_name(self, interface_name: str) -> str:
        """Get Swift class name for an interface.

        Args:
            interface_name: Name of the interface

        Returns:
            Swift class name (remove I prefix if present)
        """
        if interface_name.startswith("I") and len(interface_name) > 1:
            return interface_name[1:]
        return interface_name

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

    def is_interface(self, type_spec: Type) -> bool:
        """Check if type is an interface reference."""
        if isinstance(type_spec, NullableType):
            return self.is_interface(type_spec.inner_type)
        return isinstance(type_spec, TypeRef) and type_spec.name not in self.enum_names

    def is_enum(self, type_spec: Type) -> bool:
        """Check if type is an enum."""
        if isinstance(type_spec, NullableType):
            return self.is_enum(type_spec.inner_type)
        return isinstance(type_spec, TypeRef) and type_spec.name in self.enum_names

    def needs_optional(self, type_spec: Type) -> bool:
        """Check if type needs optional handling in Swift."""
        # Nullable types and strings from C need optional handling
        return self.is_nullable(type_spec) or self.is_string(type_spec)

    def c_to_swift_value(
        self, var_name: str, type_spec: Type, indent: str = "    "
    ) -> str:
        """Generate code to convert C value to Swift value.

        Args:
            var_name: Variable name containing C value
            type_spec: Type specification
            indent: Indentation string

        Returns:
            Swift code for conversion
        """
        if self.is_string(type_spec):
            return f"String(cString: {var_name}!)"
        elif self.is_primitive(type_spec) or self.is_enum(type_spec):
            return var_name
        elif self.is_interface(type_spec):
            class_name = self.swift_class_name(
                type_spec.name if isinstance(type_spec, TypeRef) else "Unknown"
            )
            return f"{class_name}(handle: {var_name}!)"
        elif self.is_array(type_spec):
            # Complex array conversion - would need to be in template
            return f"// TODO: Convert array {var_name}"
        else:
            return var_name

    def swift_to_c_value(self, var_name: str, type_spec: Type) -> str:
        """Generate code to convert Swift value to C value.

        Args:
            var_name: Variable name containing Swift value
            type_spec: Type specification

        Returns:
            C value expression
        """
        if self.is_string(type_spec):
            return var_name
        elif self.is_primitive(type_spec) or self.is_enum(type_spec):
            return var_name
        elif self.is_interface(type_spec):
            if self.is_nullable(type_spec):
                return f"{var_name}?.handle"
            else:
                return f"{var_name}.handle"
        else:
            return var_name

    def swift_to_c_param(self, param_name: str, param_type: Type) -> str:
        """Generate Swift to C parameter conversion.
        
        Args:
            param_name: Parameter name
            param_type: Parameter type
            
        Returns:
            C parameter expression
        """
        if self.is_enum(param_type):
            return f"{param_name}.cValue"
        return self.swift_to_c_value(param_name, param_type)

    def render_expression(self, expr: Expression) -> str:
        """Render an expression to Swift code.

        Args:
            expr: Expression AST node

        Returns:
            Swift expression string
        """
        if isinstance(expr, LiteralExpression):
            if expr.base == "hex":
                return f"0x{expr.value:X}"
            elif expr.base == "binary":
                return f"0b{expr.value:b}"
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

        # Fallback for direct values
        return str(expr)

    def generate(self, idl_file: IDLFile, output_dir: Path) -> list[Path]:
        """Generate Swift bindings from AST.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Directory to write generated files

        Returns:
            List of generated file paths
        """
        generated_files = []

        # For each namespace, create a Swift package
        for namespace in idl_file.namespaces:
            self.namespace_name = namespace.name
            self.c_gen.namespace_prefix = namespace.name
            self.enum_names = {enum.name for enum in namespace.enums}
            self.c_gen.enum_names = self.enum_names

            # Create package directory
            package_dir = output_dir / namespace.name
            package_dir.mkdir(parents=True, exist_ok=True)

            # Create Sources directory
            sources_dir = package_dir / "Sources" / namespace.name
            sources_dir.mkdir(parents=True, exist_ok=True)

            # Create C wrapper module directory
            c_module_dir = package_dir / "Sources" / f"{namespace.name}C"
            c_module_dir.mkdir(parents=True, exist_ok=True)

            # Generate Package.swift
            package_template = self.get_template("swift/Package.swift.j2")
            package_content = package_template.render(namespace=namespace)
            package_path = self.write_file(
                package_dir, "Package.swift", package_content
            )
            generated_files.append(package_path)

            # Generate Types.swift (enums and typedefs)
            types_template = self.get_template("swift/Types.swift.j2")
            types_content = types_template.render(namespace=namespace)
            types_path = self.write_file(sources_dir, "Types.swift", types_content)
            generated_files.append(types_path)

            # Generate wrapper classes
            wrapper_template = self.get_template("swift/wrapper.swift.j2")
            wrapper_content = wrapper_template.render(namespace=namespace)
            wrapper_path = self.write_file(
                sources_dir, f"{namespace.name}.swift", wrapper_content
            )
            generated_files.append(wrapper_path)

            # Generate module map
            modulemap_template = self.get_template("swift/module.modulemap.j2")
            modulemap_content = modulemap_template.render(namespace=namespace)
            modulemap_path = self.write_file(
                c_module_dir, "module.modulemap", modulemap_content
            )
            generated_files.append(modulemap_path)

            # Generate README
            readme_template = self.get_template("swift/README.md.j2")
            readme_content = readme_template.render(namespace=namespace)
            readme_path = self.write_file(package_dir, "README.md", readme_content)
            generated_files.append(readme_path)

            # Create Tests directory
            tests_dir = package_dir / "Tests" / f"{namespace.name}Tests"
            tests_dir.mkdir(parents=True, exist_ok=True)

            # Generate basic tests
            basic_tests_template = self.get_template("swift/BasicTests.swift.j2")
            basic_tests_content = basic_tests_template.render(namespace=namespace)
            basic_tests_path = self.write_file(
                tests_dir, f"{namespace.name}Tests.swift", basic_tests_content
            )
            generated_files.append(basic_tests_path)

        return generated_files

    def get_output_filename(self, namespace_name: str) -> str:
        """Get output filename for a namespace.

        Args:
            namespace_name: Name of the namespace

        Returns:
            Output filename
        """
        return namespace_name
