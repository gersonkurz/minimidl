"""JSON serialization for AST nodes."""

import json
from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel

from minimidl.ast.nodes import IDLFile


def save_ast(ast: IDLFile, path: Union[str, Path]) -> None:
    """Save AST to JSON file.

    Args:
        ast: The AST to save.
        path: Path to save the JSON file.
    """
    path = Path(path)
    
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON with Pydantic
    json_data = ast.model_dump(mode="json", exclude_none=True)
    
    # Write with pretty formatting
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def load_ast(path: Union[str, Path]) -> IDLFile:
    """Load AST from JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        The loaded AST.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the JSON is invalid.
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"AST file not found: {path}")
    
    # Read JSON data
    with open(path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    # Convert back to AST using Pydantic
    return IDLFile.model_validate(json_data)


def ast_to_dict(ast: BaseModel) -> dict[str, Any]:
    """Convert AST node to dictionary representation.

    Args:
        ast: AST node to convert.

    Returns:
        Dictionary representation of the AST.
    """
    return ast.model_dump(mode="json", exclude_none=True)


def dict_to_ast(data: dict[str, Any], model_class: type[BaseModel]) -> BaseModel:
    """Convert dictionary to AST node.

    Args:
        data: Dictionary data.
        model_class: The Pydantic model class to instantiate.

    Returns:
        The AST node.
    """
    return model_class.model_validate(data)