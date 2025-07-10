"""C++ code generator for MinimIDL."""

from pathlib import Path
from typing import Any

from minimidl.ast.nodes import (
    ArrayType,
    BinaryExpression,
    DictType,
    Expression,
    IdentifierExpression,
    IDLFile,
    LiteralExpression,
    NullableType,
    ParenthesizedExpression,
    PrimitiveType,
    SetType,
    Type,
    TypeRef,
    UnaryExpression,
)
from minimidl.generators.base import BaseGenerator


class CppGenerator(BaseGenerator):
    """Generate C++ code from MinimIDL AST."""

    def get_custom_filters(self) -> dict[str, Any]:
        """Get C++ specific Jinja2 filters."""
        return {
            "cpp_type": self.cpp_type,
            "cpp_param_type": self.cpp_param_type,
            "render_expression": self.render_expression,
        }

    def cpp_type(self, type_spec: Type) -> str:
        """Convert IDL type to C++ type.

        Args:
            type_spec: IDL type specification

        Returns:
            C++ type string
        """
        if isinstance(type_spec, PrimitiveType):
            type_map = {
                "void": "void",
                "bool": "bool",
                "int32_t": "int32_t",
                "int64_t": "int64_t",
                "float": "float",
                "double": "double",
                "string_t": "std::string",
            }
            return type_map.get(type_spec.name, type_spec.name)

        elif isinstance(type_spec, TypeRef):
            # Could be enum or interface reference
            return type_spec.name

        elif isinstance(type_spec, ArrayType):
            element_type = self.cpp_type(type_spec.element_type)
            return f"std::vector<{element_type}>"

        elif isinstance(type_spec, DictType):
            key_type = self.cpp_type(type_spec.key_type)
            value_type = self.cpp_type(type_spec.value_type)
            return f"std::unordered_map<{key_type}, {value_type}>"

        elif isinstance(type_spec, SetType):
            element_type = self.cpp_type(type_spec.element_type)
            return f"std::unordered_set<{element_type}>"

        elif isinstance(type_spec, NullableType):
            inner_type = self.cpp_type(type_spec.inner_type)
            # For primitives, use std::optional
            if isinstance(type_spec.inner_type, PrimitiveType):
                return f"std::optional<{inner_type}>"
            # For objects, use shared_ptr
            else:
                return f"std::shared_ptr<{inner_type}>"

        return "unknown_type"

    def cpp_param_type(self, type_spec: Type) -> str:
        """Get C++ parameter type (with const ref as needed).

        Args:
            type_spec: IDL type specification

        Returns:
            C++ parameter type string
        """
        cpp_type = self.cpp_type(type_spec)

        # Primitives are passed by value
        if isinstance(type_spec, PrimitiveType) and type_spec.name != "string_t":
            return cpp_type

        # Everything else by const reference
        return f"const {cpp_type}&"

    def render_expression(self, expr: Expression) -> str:
        """Render an expression to C++ code.

        Args:
            expr: Expression AST node

        Returns:
            C++ expression string
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

        # Fallback for direct values (from transformer)
        return str(expr)

    def generate(self, idl_file: IDLFile, output_dir: Path) -> list[Path]:
        """Generate C++ code from AST.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Directory to write generated files

        Returns:
            List of generated file paths
        """
        generated_files = []

        # Group namespaces by output file
        # For now, generate one file per namespace
        for namespace in idl_file.namespaces:
            filename = self.get_output_filename(namespace.name)

            # Render template
            template = self.get_template("cpp/interface.hpp.jinja2")
            content = template.render(namespaces=[namespace])

            # Write file
            output_path = self.write_file(output_dir, filename, content)
            generated_files.append(output_path)

        return generated_files

    def get_output_filename(self, namespace_name: str) -> str:
        """Get output filename for a namespace.

        Args:
            namespace_name: Name of the namespace

        Returns:
            Output filename
        """
        return f"{namespace_name}.hpp"
