"""Unit tests for the IDL parser."""

import pytest
from lark import ParseError, Tree

from minimidl.parser import parse_idl


class TestBasicParsing:
    """Test basic IDL parsing functionality."""

    def test_empty_namespace(self) -> None:
        """Test parsing an empty namespace."""
        idl = "namespace Test {}"
        tree = parse_idl(idl, transform=False)
        assert isinstance(tree, Tree)
        assert tree.data == "start"
        assert len(tree.children) == 1
        assert tree.children[0].data == "namespace_decl"

    def test_multiple_namespaces(self) -> None:
        """Test parsing multiple namespaces."""
        idl = """
        namespace First {}
        namespace Second {}
        """
        tree = parse_idl(idl, transform=False)
        assert len(tree.children) == 2
        assert all(child.data == "namespace_decl" for child in tree.children)

    def test_comments_ignored(self) -> None:
        """Test that comments are properly ignored."""
        idl = """
        // This is a comment
        namespace Test {
            // Another comment
        }
        // Final comment
        """
        tree = parse_idl(idl, transform=False)
        assert len(tree.children) == 1


class TestInterfaceDeclarations:
    """Test interface declaration parsing."""

    def test_empty_interface(self) -> None:
        """Test parsing an empty interface."""
        idl = """
        namespace Test {
            interface IEmpty {}
        }
        """
        tree = parse_idl(idl, transform=False)
        ns_body = tree.children[0].children[1]
        interface = ns_body.children[0]
        assert interface.data == "interface_decl"
        assert interface.children[0].value == "IEmpty"  # type: ignore[union-attr]

    def test_interface_with_methods(self) -> None:
        """Test parsing interface with methods."""
        idl = """
        namespace Test {
            interface ICalculator {
                double Add(double a, double b);
                double Subtract(double a, double b);
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        ns_body = tree.children[0].children[1]
        interface = ns_body.children[0]
        assert len(interface.children) == 3  # name + 2 methods

    def test_interface_with_properties(self) -> None:
        """Test parsing interface with properties."""
        idl = """
        namespace Test {
            interface IConfig {
                int32_t Count;
                string_t Name writable;
                bool IsEnabled;
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        ns_body = tree.children[0].children[1]
        interface = ns_body.children[0]
        members = [child for child in interface.children if hasattr(child, "data")]
        assert len(members) == 3

    def test_forward_declaration(self) -> None:
        """Test parsing forward declarations."""
        idl = """
        namespace Test {
            interface IForward;
            interface IUser {
                IForward GetForward();
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        ns_body = tree.children[0].children[1]
        assert ns_body.children[0].data == "forward_decl"
        assert ns_body.children[1].data == "interface_decl"


class TestTypeSystem:
    """Test type system parsing."""

    def test_primitive_types(self) -> None:
        """Test parsing all primitive types."""
        idl = """
        namespace Test {
            interface ITypes {
                bool GetBool();
                int32_t GetInt32();
                int64_t GetInt64();
                float GetFloat();
                double GetDouble();
                string_t GetString();
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_nullable_types(self) -> None:
        """Test parsing nullable types."""
        idl = """
        namespace Test {
            interface INullable {
                string_t? GetOptionalString();
                IUser? FindUser(string_t name);
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_array_types(self) -> None:
        """Test parsing array types."""
        idl = """
        namespace Test {
            interface IArrays {
                int32_t[] GetNumbers();
                string_t[] GetNames();
                IUser[] GetUsers();
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_dict_types(self) -> None:
        """Test parsing dictionary types."""
        idl = """
        namespace Test {
            interface IDicts {
                dict<int32_t, string_t> GetMapping();
                dict<string_t, IUser> GetUserMap();
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_set_types(self) -> None:
        """Test parsing set types."""
        idl = """
        namespace Test {
            interface ISets {
                set<int32_t> GetUniqueNumbers();
                set<string_t> GetUniqueNames();
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None


class TestEnumDeclarations:
    """Test enum declaration parsing."""

    def test_simple_enum(self) -> None:
        """Test parsing a simple enum."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                UNKNOWN = 0,
                ACTIVE = 1,
                INACTIVE = 2
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_enum_with_hex_values(self) -> None:
        """Test parsing enum with hex values."""
        idl = """
        namespace Test {
            enum Colors : int32_t {
                RED = 0xFF0000,
                GREEN = 0x00FF00,
                BLUE = 0x0000FF
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_enum_with_binary_values(self) -> None:
        """Test parsing enum with binary values."""
        idl = """
        namespace Test {
            enum Flags : int32_t {
                NONE = 0b0000,
                READ = 0b0001,
                WRITE = 0b0010,
                EXECUTE = 0b0100
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_enum_with_bit_shifting(self) -> None:
        """Test parsing enum with bit shifting expressions."""
        idl = """
        namespace Test {
            enum Permissions : int32_t {
                NONE = 0,
                READ = (1 << 0),
                WRITE = (1 << 1),
                EXECUTE = (1 << 2),
                ALL = (1 << 3) - 1
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_enum_trailing_comma(self) -> None:
        """Test parsing enum with trailing comma."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                ACTIVE = 1,
                INACTIVE = 2,
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None


class TestConstantDeclarations:
    """Test constant declaration parsing."""

    def test_simple_constants(self) -> None:
        """Test parsing simple constants."""
        idl = """
        namespace Test {
            const int32_t MAX_SIZE = 100;
            const int32_t MIN_SIZE = 0;
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_hex_constants(self) -> None:
        """Test parsing hex constants."""
        idl = """
        namespace Test {
            const int32_t MASK = 0xFF;
            const int64_t BIG_MASK = 0xFFFFFFFF;
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_binary_constants(self) -> None:
        """Test parsing binary constants."""
        idl = """
        namespace Test {
            const int32_t FLAGS = 0b11010010;
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_expression_constants(self) -> None:
        """Test parsing constants with expressions."""
        idl = """
        namespace Test {
            const int32_t SHIFTED = (1 << 8);
            const int32_t COMBINED = (1 << 8) | 0xFF;
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None


class TestTypedefDeclarations:
    """Test typedef declaration parsing."""

    def test_simple_typedef(self) -> None:
        """Test parsing simple typedefs."""
        idl = """
        namespace Test {
            typedef int32_t UserId;
            typedef string_t UserName;
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_typedef_arrays(self) -> None:
        """Test parsing typedef with arrays."""
        idl = """
        namespace Test {
            typedef int32_t[] NumberList;
            typedef string_t[] NameList;
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None


class TestComplexScenarios:  # pylint: disable=too-few-public-methods
    """Test complex IDL scenarios."""

    def test_complete_example(self) -> None:
        """Test parsing a complete example with multiple constructs."""
        idl = """
        namespace PaymentAPI {
            // Forward declarations
            interface IPaymentResult;

            // Type aliases
            typedef string_t CardNumber;
            typedef double Amount;

            // Constants
            const int32_t MAX_RETRIES = 3;
            const int32_t TIMEOUT_MS = 5000;

            // Enums
            enum PaymentStatus : int32_t {
                PENDING = 0,
                PROCESSING = 1,
                COMPLETED = 2,
                FAILED = 3
            }

            enum PaymentMethod : int32_t {
                CARD = (1 << 0),
                BANK = (1 << 1),
                WALLET = (1 << 2)
            }

            // Main interface
            interface IPaymentProcessor {
                // Properties
                int32_t TransactionCount;
                string_t MerchantId writable;

                // Methods
                bool ProcessPayment(CardNumber cardNumber, Amount amount);
                string_t[] GetSupportedCurrencies();
                IPaymentResult? GetLastResult();
                dict<string_t, double> GetExchangeRates();
                set<int32_t> GetSupportedMethods();
            }

            // Result interface
            interface IPaymentResult {
                PaymentStatus Status;
                string_t TransactionId;
                string_t? ErrorMessage;
                double ProcessingTime;
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None
        assert len(tree.children) == 1  # One namespace


class TestErrorHandling:
    """Test parser error handling."""

    def test_invalid_syntax(self) -> None:
        """Test that invalid syntax raises ParseError."""
        idl = "this is not valid IDL"
        with pytest.raises(ParseError):
            parse_idl(idl, transform=False)

    def test_missing_semicolon(self) -> None:
        """Test that missing semicolons are caught."""
        idl = """
        namespace Test {
            interface ITest {
                void Method()  // Missing semicolon
            }
        }
        """
        with pytest.raises(ParseError):
            parse_idl(idl, transform=False)

    def test_invalid_type(self) -> None:
        """Test that invalid types are caught."""
        idl = """
        namespace Test {
            interface ITest {
                invalid_type GetValue();
            }
        }
        """
        # Note: This will parse successfully as IDENTIFIER
        # Type validation would happen in a later phase
        tree = parse_idl(idl, transform=False)
        assert tree is not None

    def test_unclosed_namespace(self) -> None:
        """Test that unclosed namespaces are caught."""
        idl = """
        namespace Test {
            interface ITest {}
        // Missing closing brace
        """
        with pytest.raises(ParseError):
            parse_idl(idl, transform=False)

    def test_duplicate_enum_values(self) -> None:
        """Test that duplicate enum values parse (validation is semantic)."""
        idl = """
        namespace Test {
            enum Status : int32_t {
                FIRST = 1,
                SECOND = 1  // Duplicate value - parser allows, semantic check later
            }
        }
        """
        tree = parse_idl(idl, transform=False)
        assert tree is not None
