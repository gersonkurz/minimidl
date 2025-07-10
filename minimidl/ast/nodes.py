"""AST node definitions for MinimIDL using Pydantic."""

from abc import ABC
from enum import Enum as PyEnum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ASTNode(BaseModel, ABC):
    """Base class for all AST nodes."""

    line: Optional[int] = None
    column: Optional[int] = None

    model_config = ConfigDict(
        extra="forbid",  # Strict validation
        validate_assignment=True,
    )


class Expression(ASTNode, ABC):
    """Base class for expressions (used in constants and enums)."""

    pass


class LiteralExpression(Expression):
    """Literal value expression."""

    value: Union[int, float, str]
    base: Optional[str] = None  # "hex", "binary", or None for decimal


class IdentifierExpression(Expression):
    """Identifier reference expression."""

    name: str


class BinaryExpression(Expression):
    """Binary operation expression."""

    operator: str  # "+", "-", "*", "/", "%", "<<", ">>", "&", "|"
    left: Expression
    right: Expression


class UnaryExpression(Expression):
    """Unary operation expression."""

    operator: str  # "+", "-", "~"
    operand: Expression


class ParenthesizedExpression(Expression):
    """Parenthesized expression."""

    expression: Expression


class Type(ASTNode, ABC):
    """Base class for all type specifications."""

    pass


class PrimitiveType(Type):
    """Built-in primitive types."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_primitive(cls, v: str) -> str:
        """Validate primitive type name."""
        valid_types = {"void", "bool", "int32_t", "int64_t", "float", "double", "string_t"}
        if v not in valid_types:
            raise ValueError(f"Invalid primitive type: {v}")
        return v


class TypeRef(Type):
    """Reference to a user-defined type (interface, enum, typedef)."""

    name: str


class ArrayType(Type):
    """Array type specification."""

    element_type: Type


class DictType(Type):
    """Dictionary type specification."""

    key_type: Type
    value_type: Type


class SetType(Type):
    """Set type specification."""

    element_type: Type


class NullableType(Type):
    """Nullable type wrapper."""

    inner_type: Type


class Parameter(ASTNode):
    """Method parameter definition."""

    name: str
    type: Type


class Method(ASTNode):
    """Interface method definition."""

    name: str
    return_type: Type
    parameters: list[Parameter] = Field(default_factory=list)


class Property(ASTNode):
    """Interface property definition."""

    name: str
    type: Type
    writable: bool = False


class Interface(ASTNode):
    """Interface definition."""

    name: str
    methods: list[Method] = Field(default_factory=list)
    properties: list[Property] = Field(default_factory=list)


class ForwardDeclaration(ASTNode):
    """Forward declaration of an interface."""

    name: str


class EnumValue(ASTNode):
    """Enum member definition."""

    name: str
    value: Expression


class Enum(ASTNode):
    """Enum definition."""

    name: str
    backing_type: str  # int32_t or int64_t
    values: list[EnumValue] = Field(default_factory=list)

    @field_validator("backing_type")
    @classmethod
    def validate_backing_type(cls, v: str) -> str:
        """Validate enum backing type."""
        if v not in ("int32_t", "int64_t"):
            raise ValueError(f"Invalid enum backing type: {v}")
        return v


class Typedef(ASTNode):
    """Type alias definition."""

    name: str
    type: Type


class ConstantValue(ASTNode):
    """Constant value definition."""

    type: str  # int32_t, int64_t, float, double
    value: Expression

    @field_validator("type")
    @classmethod
    def validate_const_type(cls, v: str) -> str:
        """Validate constant type."""
        valid_types = {"int32_t", "int64_t", "float", "double"}
        if v not in valid_types:
            raise ValueError(f"Invalid constant type: {v}")
        return v


class Constant(ASTNode):
    """Constant definition."""

    name: str
    constant_value: ConstantValue


class NamespaceContent(ASTNode):
    """Content that can appear in a namespace."""

    pass


class Namespace(ASTNode):
    """Namespace definition."""

    name: str
    interfaces: list[Interface] = Field(default_factory=list)
    enums: list[Enum] = Field(default_factory=list)
    typedefs: list[Typedef] = Field(default_factory=list)
    constants: list[Constant] = Field(default_factory=list)
    forward_declarations: list[ForwardDeclaration] = Field(default_factory=list)


class IDLFile(ASTNode):
    """Root AST node representing an entire IDL file."""

    namespaces: list[Namespace] = Field(default_factory=list)
    source_file: Optional[str] = None


# Type aliases for better readability
AnyType = Union[PrimitiveType, TypeRef, ArrayType, DictType, SetType, NullableType]
AnyExpression = Union[
    LiteralExpression,
    IdentifierExpression,
    BinaryExpression,
    UnaryExpression,
    ParenthesizedExpression,
]