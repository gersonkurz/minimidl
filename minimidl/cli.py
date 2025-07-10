"""MinimIDL command-line interface."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger

from minimidl.ast.validator import SemanticValidator
from minimidl.generators.cpp import CppGenerator
from minimidl.parser import IDLParser

app = typer.Typer(
    name="minimidl",
    help="Modern Interface Definition Language compiler",
    add_completion=False,
)


@app.command()
def parse(
    idl_file: Annotated[Path, typer.Argument(help="IDL file to parse", exists=True)],
    json: Annotated[bool, typer.Option("--json", help="Output AST as JSON")] = False,
) -> None:
    """Parse an IDL file and display the AST."""
    try:
        # Read IDL file
        content = idl_file.read_text()

        # Parse
        parser = IDLParser()
        ast = parser.parse(content)

        # Validate
        validator = SemanticValidator()
        errors = validator.validate(ast)

        if errors:
            typer.echo("Validation errors:", err=True)
            for error in errors:
                typer.echo(f"  {error}", err=True)
            raise typer.Exit(1)

        # Output
        if json:
            import json as json_lib

            typer.echo(json_lib.dumps(ast.model_dump(), indent=2))
        else:
            typer.echo(f"Successfully parsed {idl_file}")
            typer.echo(f"Namespaces: {len(ast.namespaces)}")
            for ns in ast.namespaces:
                typer.echo(f"  - {ns.name}:")
                typer.echo(f"    Interfaces: {len(ns.interfaces)}")
                typer.echo(f"    Enums: {len(ns.enums)}")
                typer.echo(f"    Typedefs: {len(ns.typedefs)}")
                typer.echo(f"    Constants: {len(ns.constants)}")

    except Exception as e:
        logger.exception("Failed to parse IDL file")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def generate(
    idl_file: Annotated[Path, typer.Argument(help="IDL file to compile", exists=True)],
    output_dir: Annotated[
        Path, typer.Option("-o", "--output", help="Output directory")
    ] = Path("."),
    language: Annotated[
        str, typer.Option("-l", "--language", help="Target language")
    ] = "cpp",
    template_dir: Annotated[
        Optional[Path],
        typer.Option("-t", "--templates", help="Custom template directory"),
    ] = None,
) -> None:
    """Generate code from an IDL file."""
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read and parse IDL file
        content = idl_file.read_text()
        parser = IDLParser()
        ast = parser.parse(content)

        # Validate
        validator = SemanticValidator()
        errors = validator.validate(ast)

        if errors:
            typer.echo("Validation errors:", err=True)
            for error in errors:
                typer.echo(f"  {error}", err=True)
            raise typer.Exit(1)

        # Generate code based on language
        if language == "cpp":
            generator = CppGenerator(template_dir=template_dir)
        else:
            typer.echo(f"Unsupported language: {language}", err=True)
            typer.echo("Supported languages: cpp")
            raise typer.Exit(1)

        # Generate files
        generated_files = generator.generate(ast, output_dir)

        # Report results
        typer.echo(f"Successfully generated {len(generated_files)} files:")
        for file in generated_files:
            typer.echo(f"  - {file}")

    except Exception as e:
        logger.exception("Failed to generate code")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


def main() -> int:
    """Main entry point."""
    app()
    return 0


if __name__ == "__main__":
    main()
