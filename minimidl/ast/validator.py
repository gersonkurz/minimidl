"""Semantic validation for AST nodes."""

from typing import Any

from loguru import logger

from minimidl.ast.nodes import (
    Constant,
    Enum,
    ForwardDeclaration,
    IDLFile,
    Interface,
    Method,
    Namespace,
    Parameter,
    Property,
    Type,
    Typedef,
    TypeRef,
)


class ValidationError(Exception):
    """Semantic validation error."""

    def __init__(self, message: str, node: Any = None) -> None:
        """Initialize validation error."""
        super().__init__(message)
        self.node = node


class SemanticValidator:
    """Validate AST for semantic correctness."""

    def __init__(self) -> None:
        """Initialize validator."""
        self.type_registry: dict[str, Any] = {}
        self.current_namespace: str | None = None
        self.errors: list[ValidationError] = []

    def validate(self, ast: IDLFile) -> None:
        """Validate an IDL AST.

        Args:
            ast: The AST to validate.

        Raises:
            ValidationError: If semantic errors are found.
        """
        self.errors.clear()
        self.type_registry.clear()

        # First pass: register all types
        for namespace in ast.namespaces:
            self._register_namespace_types(namespace)

        # Second pass: validate references and semantics
        for namespace in ast.namespaces:
            self._validate_namespace(namespace)

        if self.errors:
            # Report all errors
            error_msg = "Semantic validation failed with {} error(s):\n".format(
                len(self.errors)
            )
            for error in self.errors:
                error_msg += f"  - {error}\n"
            raise ValidationError(error_msg)

    def _register_namespace_types(self, namespace: Namespace) -> None:
        """Register all types defined in a namespace."""
        self.current_namespace = namespace.name

        # Register forward declarations
        for forward in namespace.forward_declarations:
            self._register_type(forward.name, "interface")

        # Register interfaces
        for interface in namespace.interfaces:
            self._register_type(interface.name, "interface")

        # Register enums
        for enum in namespace.enums:
            self._register_type(enum.name, "enum")

        # Register typedefs
        for typedef in namespace.typedefs:
            self._register_type(typedef.name, "typedef")

    def _register_type(self, name: str, kind: str) -> None:
        """Register a type in the registry."""
        full_name = f"{self.current_namespace}::{name}"

        if full_name in self.type_registry:
            # Check if it's a forward declaration being defined
            if self.type_registry[full_name] == "interface" and kind == "interface":
                # This is OK - forward declaration being defined
                return

            self.errors.append(ValidationError(f"Duplicate type definition: {name}"))
        else:
            self.type_registry[full_name] = kind
            # Also register without namespace for local lookups
            self.type_registry[name] = kind
            logger.debug(f"Registered type: {full_name} ({kind})")

    def _validate_namespace(self, namespace: Namespace) -> None:
        """Validate a namespace and its contents."""
        self.current_namespace = namespace.name

        # Validate all interfaces
        for interface in namespace.interfaces:
            self._validate_interface(interface)

        # Validate all enums
        for enum in namespace.enums:
            self._validate_enum(enum)

        # Validate all constants
        for constant in namespace.constants:
            self._validate_constant(constant)

        # Validate all typedefs
        for typedef in namespace.typedefs:
            self._validate_typedef(typedef)

    def _validate_interface(self, interface: Interface) -> None:
        """Validate an interface."""
        # Check for duplicate method names
        method_names = set()
        for method in interface.methods:
            if method.name in method_names:
                self.errors.append(
                    ValidationError(
                        f"Duplicate method name '{method.name}' in interface {interface.name}",
                        method,
                    )
                )
            method_names.add(method.name)

            # Validate method
            self._validate_method(method, interface.name)

        # Check for duplicate property names
        property_names = set()
        for prop in interface.properties:
            if prop.name in property_names:
                self.errors.append(
                    ValidationError(
                        f"Duplicate property name '{prop.name}' in interface {interface.name}",
                        prop,
                    )
                )
            property_names.add(prop.name)

            # Check for method/property name conflicts
            if prop.name in method_names:
                self.errors.append(
                    ValidationError(
                        f"Property '{prop.name}' conflicts with method name in interface {interface.name}",
                        prop,
                    )
                )

            # Validate property type
            self._validate_type(prop.type, f"property {prop.name}")

    def _validate_method(self, method: Method, interface_name: str) -> None:
        """Validate a method."""
        # Validate return type
        self._validate_type(method.return_type, f"return type of {method.name}")

        # Validate parameters
        param_names = set()
        for param in method.parameters:
            if param.name in param_names:
                self.errors.append(
                    ValidationError(
                        f"Duplicate parameter name '{param.name}' in method {interface_name}::{method.name}",
                        param,
                    )
                )
            param_names.add(param.name)

            # Validate parameter type
            self._validate_type(
                param.type, f"parameter '{param.name}' of {method.name}"
            )

    def _validate_type(self, type_spec: Type, context: str) -> None:
        """Validate a type reference."""
        from minimidl.ast.nodes import (
            ArrayType,
            DictType,
            NullableType,
            PrimitiveType,
            SetType,
        )

        if isinstance(type_spec, PrimitiveType):
            # Primitive types are always valid (validated by Pydantic)
            return
        elif isinstance(type_spec, TypeRef):
            # Check if type exists
            if not self._type_exists(type_spec.name):
                self.errors.append(
                    ValidationError(
                        f"Unknown type '{type_spec.name}' in {context}", type_spec
                    )
                )
        elif isinstance(type_spec, ArrayType):
            self._validate_type(type_spec.element_type, f"array element in {context}")
        elif isinstance(type_spec, DictType):
            self._validate_type(type_spec.key_type, f"dict key in {context}")
            self._validate_type(type_spec.value_type, f"dict value in {context}")
        elif isinstance(type_spec, SetType):
            self._validate_type(type_spec.element_type, f"set element in {context}")
        elif isinstance(type_spec, NullableType):
            self._validate_type(type_spec.inner_type, f"nullable type in {context}")

    def _type_exists(self, name: str) -> bool:
        """Check if a type exists in the registry."""
        # Check with namespace prefix first
        full_name = f"{self.current_namespace}::{name}"
        if full_name in self.type_registry:
            return True

        # Check without namespace (for types in same namespace)
        if name in self.type_registry:
            return True

        # Check if it's "void" (special case for return types)
        if name == "void":
            return True

        return False

    def _validate_enum(self, enum: Enum) -> None:
        """Validate an enum."""
        # Check for duplicate enum values
        value_names = set()
        for value in enum.values:
            if value.name in value_names:
                self.errors.append(
                    ValidationError(
                        f"Duplicate enum value '{value.name}' in enum {enum.name}",
                        value,
                    )
                )
            value_names.add(value.name)

        # Note: We don't validate enum value expressions here as they
        # should be evaluated during code generation

    def _validate_constant(self, constant: Constant) -> None:
        """Validate a constant."""
        # Constants are mostly validated by Pydantic
        # We could add expression validation here if needed
        pass

    def _validate_typedef(self, typedef: Typedef) -> None:
        """Validate a typedef."""
        # Validate the aliased type
        self._validate_type(typedef.type, f"typedef {typedef.name}")


def validate_ast(ast: IDLFile) -> None:
    """Validate an AST for semantic correctness.

    Args:
        ast: The AST to validate.

    Raises:
        ValidationError: If semantic errors are found.
    """
    validator = SemanticValidator()
    validator.validate(ast)
