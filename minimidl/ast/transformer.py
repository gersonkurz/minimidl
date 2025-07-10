"""Transformer to convert Lark parse tree to AST nodes."""

from typing import Any, Union

from lark import Token, Transformer, Tree

from minimidl.ast.nodes import (
    ArrayType,
    BinaryExpression,
    Constant,
    ConstantValue,
    DictType,
    Enum,
    EnumValue,
    Expression,
    ForwardDeclaration,
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
    Typedef,
    TypeRef,
    UnaryExpression,
)


class IDLTransformer(Transformer):
    """Transform Lark parse tree into AST nodes."""

    def __init__(self) -> None:
        """Initialize the transformer."""
        super().__init__()
        self.current_line = 0
        self.current_column = 0

    def _update_position(self, item: Union[Token, Tree]) -> tuple[int, int]:
        """Update and return current position from token or tree."""
        if isinstance(item, Token):
            self.current_line = item.line
            self.current_column = item.column
        elif isinstance(item, Tree) and item.meta:
            self.current_line = item.meta.line
            self.current_column = item.meta.column
        return self.current_line, self.current_column

    # Entry point
    def start(self, items: list[Namespace]) -> IDLFile:
        """Transform the root node."""
        return IDLFile(namespaces=items)

    # Namespace
    def namespace_decl(self, items: list[Any]) -> Namespace:
        """Transform namespace declaration."""
        name = items[0].value
        namespace_body = items[1]
        return Namespace(
            name=name,
            interfaces=namespace_body.get("interfaces", []),
            enums=namespace_body.get("enums", []),
            typedefs=namespace_body.get("typedefs", []),
            constants=namespace_body.get("constants", []),
            forward_declarations=namespace_body.get("forward_declarations", []),
            line=self._update_position(items[0])[0],
            column=self._update_position(items[0])[1],
        )

    def namespace_body(self, items: list[Any]) -> dict[str, list[Any]]:
        """Transform namespace body."""
        result: dict[str, list[Any]] = {
            "interfaces": [],
            "enums": [],
            "typedefs": [],
            "constants": [],
            "forward_declarations": [],
        }

        for item in items:
            if isinstance(item, Interface):
                result["interfaces"].append(item)
            elif isinstance(item, Enum):
                result["enums"].append(item)
            elif isinstance(item, Typedef):
                result["typedefs"].append(item)
            elif isinstance(item, Constant):
                result["constants"].append(item)
            elif isinstance(item, ForwardDeclaration):
                result["forward_declarations"].append(item)

        return result

    # Forward declaration
    def forward_decl(self, items: list[Any]) -> ForwardDeclaration:
        """Transform forward declaration."""
        return ForwardDeclaration(
            name=items[0].value,
            line=self._update_position(items[0])[0],
            column=self._update_position(items[0])[1],
        )

    # Interface
    def interface_decl(self, items: list[Any]) -> Interface:
        """Transform interface declaration."""
        name = items[0].value
        methods = []
        properties = []

        for item in items[1:]:
            if isinstance(item, Method):
                methods.append(item)
            elif isinstance(item, Property):
                properties.append(item)

        return Interface(
            name=name,
            methods=methods,
            properties=properties,
            line=self._update_position(items[0])[0],
            column=self._update_position(items[0])[1],
        )

    def interface_member(self, items: list[Any]) -> Union[Method, Property]:
        """Transform interface member."""
        return items[0]

    # Property
    def property_decl(self, items: list[Any]) -> Property:
        """Transform property declaration."""
        type_spec = items[0]
        name = items[1].value
        writable = len(items) > 2 and items[2] is not None

        return Property(
            name=name,
            type=type_spec,
            writable=writable,
            line=self._update_position(items[1])[0],
            column=self._update_position(items[1])[1],
        )

    def writable(self, items: list[Any]) -> bool:
        """Transform writable modifier."""
        return True

    # Method
    def method_decl(self, items: list[Any]) -> Method:
        """Transform method declaration."""
        return_type = items[0]
        name = items[1].value
        parameters = items[2] if len(items) > 2 and items[2] else []

        return Method(
            name=name,
            return_type=return_type,
            parameters=parameters,
            line=self._update_position(items[1])[0],
            column=self._update_position(items[1])[1],
        )

    def parameter_list(self, items: list[Parameter]) -> list[Parameter]:
        """Transform parameter list."""
        return items

    def parameter(self, items: list[Any]) -> Parameter:
        """Transform parameter."""
        return Parameter(
            type=items[0],
            name=items[1].value,
            line=self._update_position(items[1])[0],
            column=self._update_position(items[1])[1],
        )

    # Enum
    def enum_decl(self, items: list[Any]) -> Enum:
        """Transform enum declaration."""
        name = items[0].value
        # backing_type is now a PrimitiveType object
        backing_type = (
            items[1].name if isinstance(items[1], PrimitiveType) else items[1].value
        )
        values = items[2] if len(items) > 2 and items[2] else []

        return Enum(
            name=name,
            backing_type=backing_type,
            values=values,
            line=self._update_position(items[0])[0],
            column=self._update_position(items[0])[1],
        )

    def enum_member_list(self, items: list[EnumValue]) -> list[EnumValue]:
        """Transform enum member list."""
        return items

    def enum_member(self, items: list[Any]) -> EnumValue:
        """Transform enum member."""
        return EnumValue(
            name=items[0].value,
            value=items[1],
            line=self._update_position(items[0])[0],
            column=self._update_position(items[0])[1],
        )

    # Typedef
    def typedef_decl(self, items: list[Any]) -> Typedef:
        """Transform typedef declaration."""
        return Typedef(
            type=items[0],
            name=items[1].value,
            line=self._update_position(items[1])[0],
            column=self._update_position(items[1])[1],
        )

    # Constant
    def const_decl(self, items: list[Any]) -> Constant:
        """Transform constant declaration."""
        # type is now a PrimitiveType object
        type_name = (
            items[0].name if isinstance(items[0], PrimitiveType) else items[0].value
        )
        name = items[1].value
        value = items[2]

        return Constant(
            name=name,
            constant_value=ConstantValue(type=type_name, value=value),
            line=self._update_position(items[1])[0],
            column=self._update_position(items[1])[1],
        )

    # Types
    def type_spec(self, items: list[Type]) -> Type:
        """Transform type specification."""
        return items[0]

    def nullable_type(self, items: list[Type]) -> NullableType:
        """Transform nullable type."""
        return NullableType(inner_type=items[0])

    def non_nullable_type(self, items: list[Type]) -> Type:
        """Transform non-nullable type."""
        return items[0]

    def array_type(self, items: list[Type]) -> ArrayType:
        """Transform array type."""
        return ArrayType(element_type=items[0])

    def dict_type(self, items: list[Type]) -> DictType:
        """Transform dictionary type."""
        return DictType(key_type=items[0], value_type=items[1])

    def set_type(self, items: list[Type]) -> SetType:
        """Transform set type."""
        return SetType(element_type=items[0])

    def basic_type(self, items: list[Any]) -> Type:
        """Transform basic type."""
        item = items[0]
        if isinstance(item, Token) and item.type == "IDENTIFIER":
            return TypeRef(name=item.value)
        return item

    def primitive_type(self, items: list[Token]) -> PrimitiveType:
        """Transform primitive type."""
        token = items[0]
        # Map token types to primitive names
        type_map = {
            "VOID": "void",
            "BOOL": "bool",
            "INT32": "int32_t",
            "INT64": "int64_t",
            "FLOAT": "float",
            "DOUBLE": "double",
        }
        return PrimitiveType(name=type_map.get(token.type, token.value))

    def string_type(self, items: list[Token]) -> PrimitiveType:
        """Transform string type."""
        return PrimitiveType(name="string_t")

    # Expressions
    def expression(self, items: list[Expression]) -> Expression:
        """Transform expression."""
        return items[0]

    def or_expr(self, items: list[Expression]) -> Expression:
        """Transform OR expression."""
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items)):
            result = BinaryExpression(operator="|", left=result, right=items[i])
        return result

    def and_expr(self, items: list[Expression]) -> Expression:
        """Transform AND expression."""
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items)):
            result = BinaryExpression(operator="&", left=result, right=items[i])
        return result

    def shift_expr(self, items: list[Any]) -> Expression:
        """Transform shift expression."""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            # Handle case where we only have operator and right operand
            if isinstance(items[0], Token):
                return UnaryExpression(operator=items[0].value, operand=items[1])
            else:
                return items[0]
        result = items[0]
        i = 1
        while i < len(items) - 1:
            op = items[i].value if isinstance(items[i], Token) else items[i]
            result = BinaryExpression(operator=op, left=result, right=items[i + 1])
            i += 2
        return result

    def add_expr(self, items: list[Any]) -> Expression:
        """Transform addition/subtraction expression."""
        if len(items) == 1:
            return items[0]
        result = items[0]
        i = 1
        while i < len(items) - 1:
            op = items[i].value if isinstance(items[i], Token) else items[i]
            result = BinaryExpression(operator=op, left=result, right=items[i + 1])
            i += 2
        return result

    def mul_expr(self, items: list[Any]) -> Expression:
        """Transform multiplication/division expression."""
        if len(items) == 1:
            return items[0]
        result = items[0]
        i = 1
        while i < len(items) - 1:
            op = items[i].value if isinstance(items[i], Token) else items[i]
            result = BinaryExpression(operator=op, left=result, right=items[i + 1])
            i += 2
        return result

    def unary_expr(self, items: list[Any]) -> Expression:
        """Transform unary expression."""
        if len(items) == 1:
            return items[0]
        operator = items[0].value if isinstance(items[0], Token) else items[0]
        return UnaryExpression(operator=operator, operand=items[1])

    def primary_expr(self, items: list[Any]) -> Expression:
        """Transform primary expression."""
        if len(items) == 3:  # Parenthesized expression
            return items[1]  # Return the inner expression directly
        elif isinstance(items[0], Expression):
            return items[0]
        elif isinstance(items[0], Token):
            if items[0].type == "IDENTIFIER":
                return IdentifierExpression(name=items[0].value)
        return items[0]

    def number(self, items: list[Token]) -> LiteralExpression:
        """Transform number literal."""
        token = items[0]
        value_str = token.value
        base = None

        if token.type == "HEX_NUMBER":
            value = int(value_str, 16)
            base = "hex"
        elif token.type == "BINARY_NUMBER":
            value = int(value_str, 2)
            base = "binary"
        else:  # DECIMAL_NUMBER
            value = int(value_str)

        return LiteralExpression(value=value, base=base)

    # Handle identifiers - return the token itself for non-type contexts
    def IDENTIFIER(self, token: Token) -> Token:
        """Return identifier token as-is."""
        return token
