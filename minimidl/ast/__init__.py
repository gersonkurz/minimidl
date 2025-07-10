"""AST node definitions and serialization for MinimIDL."""

from minimidl.ast.nodes import (
    ArrayType,
    ASTNode,
    Constant,
    ConstantValue,
    DictType,
    Enum,
    EnumValue,
    Expression,
    ForwardDeclaration,
    IDLFile,
    Interface,
    Method,
    Namespace,
    NullableType,
    Parameter,
    PrimitiveType,
    Property,
    SetType,
    Type,
    TypeRef,
    Typedef,
)
from minimidl.ast.serialization import load_ast, save_ast
from minimidl.ast.validator import ValidationError, validate_ast

__all__ = [
    # Base classes
    "ASTNode",
    "Type",
    "Expression",
    # Main declarations
    "IDLFile",
    "Namespace",
    "Interface",
    "Enum",
    "Typedef",
    "Constant",
    "ForwardDeclaration",
    # Interface members
    "Method",
    "Property",
    "Parameter",
    # Types
    "PrimitiveType",
    "TypeRef",
    "ArrayType",
    "DictType",
    "SetType",
    "NullableType",
    # Values
    "EnumValue",
    "ConstantValue",
    # Serialization
    "save_ast",
    "load_ast",
    # Validation
    "validate_ast",
    "ValidationError",
]