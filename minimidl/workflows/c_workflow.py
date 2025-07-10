"""C wrapper project generation workflow."""

from pathlib import Path
from typing import Any

from loguru import logger

from minimidl.ast.nodes import IDLFile
from minimidl.generators.c_wrapper import CWrapperGenerator


class CWorkflow:
    """Workflow for generating C wrapper projects."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize C workflow.

        Args:
            config: Optional configuration options
        """
        self.config = config or {}
        self.generator = CWrapperGenerator()

    def generate_project(
        self, idl_file: IDLFile, output_dir: Path, project_name: str | None = None
    ) -> list[Path]:
        """Generate a C wrapper project.

        Args:
            idl_file: Parsed IDL file AST
            output_dir: Output directory for the project
            project_name: Optional project name (defaults to namespace name)

        Returns:
            List of generated file paths
        """
        logger.info(f"Generating C wrapper project in {output_dir}")
        
        # Get project name from first namespace if not provided
        if not project_name and idl_file.namespaces:
            project_name = idl_file.namespaces[0].name

        project_name = project_name or "Generated"

        # Create project structure
        project_dir = output_dir / project_name / "CWrapper"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Generate C wrapper files
        generated_files = self.generator.generate(idl_file, project_dir)

        logger.success(
            f"Generated C wrapper project with {len(generated_files)} files in {project_dir}"
        )
        return generated_files