"""IDL parser implementation using Lark."""

from pathlib import Path
from typing import Any

from lark import Lark, ParseError, Tree
from loguru import logger

# Grammar file path
GRAMMAR_FILE = Path(__file__).parent / "grammar.lark"


class IDLParser:
    """MinimIDL parser using Lark grammar."""

    def __init__(self) -> None:
        """Initialize the parser with the IDL grammar."""
        self._parser = self._create_parser()

    def _create_parser(self) -> Lark:
        """Create and configure the Lark parser.

        Returns:
            Configured Lark parser instance.
        """
        grammar_text = GRAMMAR_FILE.read_text(encoding="utf-8")
        return Lark(
            grammar_text,
            parser="lalr",
            debug=False,
            propagate_positions=True,
            maybe_placeholders=False,
        )

    def parse(self, idl_content: str) -> Tree[Any]:
        """Parse IDL content into an abstract syntax tree.

        Args:
            idl_content: IDL source code to parse.

        Returns:
            Parsed abstract syntax tree.

        Raises:
            ParseError: If the IDL content has syntax errors.
        """
        try:
            logger.debug("Parsing IDL content")
            tree = self._parser.parse(idl_content)
            logger.debug("Successfully parsed IDL content")
            return tree
        except ParseError as e:
            logger.error(f"Failed to parse IDL: {e}")
            raise

    def parse_file(self, idl_path: str | Path) -> Tree[Any]:
        """Parse an IDL file into an abstract syntax tree.

        Args:
            idl_path: Path to the IDL file.

        Returns:
            Parsed abstract syntax tree.

        Raises:
            ParseError: If the IDL content has syntax errors.
            FileNotFoundError: If the IDL file doesn't exist.
        """
        path = Path(idl_path)
        if not path.exists():
            raise FileNotFoundError(f"IDL file not found: {path}")

        logger.info(f"Parsing IDL file: {path}")
        content = path.read_text(encoding="utf-8")
        return self.parse(content)


class _ParserSingleton:  # pylint: disable=too-few-public-methods
    """Singleton holder for the parser instance."""

    _instance: IDLParser | None = None

    @classmethod
    def get_instance(cls) -> IDLParser:
        """Get or create the singleton parser instance."""
        if cls._instance is None:
            cls._instance = IDLParser()
        return cls._instance


def get_parser() -> IDLParser:
    """Get or create the singleton parser instance.

    Returns:
        The IDL parser instance.
    """
    return _ParserSingleton.get_instance()


def parse_idl(idl_content: str) -> Tree[Any]:
    """Parse IDL content into an abstract syntax tree.

    This is a convenience function that uses the singleton parser.

    Args:
        idl_content: IDL source code to parse.

    Returns:
        Parsed abstract syntax tree.

    Raises:
        ParseError: If the IDL content has syntax errors.
    """
    return get_parser().parse(idl_content)


def parse_idl_file(idl_path: str | Path) -> Tree[Any]:
    """Parse an IDL file into an abstract syntax tree.

    This is a convenience function that uses the singleton parser.

    Args:
        idl_path: Path to the IDL file.

    Returns:
        Parsed abstract syntax tree.

    Raises:
        ParseError: If the IDL content has syntax errors.
        FileNotFoundError: If the IDL file doesn't exist.
    """
    return get_parser().parse_file(idl_path)
