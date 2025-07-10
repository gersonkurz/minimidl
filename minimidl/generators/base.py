"""Base generator for code generation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger

from minimidl.ast.nodes import IDLFile


class BaseGenerator(ABC):
    """Base class for all code generators."""

    def __init__(self, template_dir: Path | None = None) -> None:
        """Initialize the generator.

        Args:
            template_dir: Directory containing Jinja2 templates.
                         If None, will use default templates.
        """
        self.template_dir = template_dir
        self._env: Environment | None = None

    @property
    def jinja_env(self) -> Environment:
        """Get or create Jinja2 environment."""
        if self._env is None:
            if self.template_dir:
                self._env = Environment(
                    loader=FileSystemLoader(self.template_dir),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
            else:
                # Use templates embedded in package
                from importlib.resources import files

                templates = files("minimidl.generators.templates")
                self._env = Environment(
                    loader=FileSystemLoader(str(templates)),
                    trim_blocks=True,
                    lstrip_blocks=True,
                )

            # Add custom filters
            self._env.filters.update(self.get_custom_filters())

        return self._env

    def get_template(self, name: str) -> Template:
        """Get a template by name.

        Args:
            name: Template filename

        Returns:
            Jinja2 template
        """
        return self.jinja_env.get_template(name)

    def get_custom_filters(self) -> dict[str, Any]:
        """Get custom Jinja2 filters for this generator.

        Returns:
            Dictionary of filter name to filter function
        """
        return {}

    @abstractmethod
    def generate(self, idl_file: IDLFile, output_dir: Path) -> list[Path]:
        """Generate code from AST.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Directory to write generated files

        Returns:
            List of generated file paths
        """
        pass

    @abstractmethod
    def get_output_filename(self, namespace_name: str) -> str:
        """Get output filename for a namespace.

        Args:
            namespace_name: Name of the namespace

        Returns:
            Output filename
        """
        pass

    def write_file(self, output_dir: Path, filename: str, content: str) -> Path:
        """Write generated content to file.

        Args:
            output_dir: Output directory
            filename: Output filename
            content: File content

        Returns:
            Path to written file
        """
        output_path = output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing {output_path}")
        output_path.write_text(content)

        return output_path
