"""MinimIDL command-line interface."""

import json as json_lib
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from minimidl import __version__
from minimidl.ast.nodes import IDLFile
from minimidl.ast.serialization import load_ast, save_ast
from minimidl.ast.validator import SemanticValidator
from minimidl.generators.c_wrapper import CWrapperGenerator
from minimidl.generators.cpp import CppGenerator
from minimidl.generators.swift import SwiftGenerator
from minimidl.parser import IDLParser
from minimidl.workflows.cpp_workflow import CppWorkflow
from minimidl.workflows.swift_workflow import SwiftWorkflow

app = typer.Typer(
    name="minimidl",
    help="Modern Interface Definition Language compiler",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"MinimIDL version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable verbose logging"),
    ] = False,
) -> None:
    """MinimIDL - Modern Interface Definition Language compiler."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")


@app.command()
def parse(
    idl_file: Annotated[Path, typer.Argument(help="IDL file to parse")],
    json: Annotated[bool, typer.Option("--json", help="Output AST as JSON")] = False,
    output: Annotated[
        Optional[Path], typer.Option("-o", "--output", help="Output file for AST")
    ] = None,
) -> None:
    """Parse an IDL file and display the AST."""
    try:
        # Validate file exists
        if not idl_file.exists():
            console.print(f"[red]Error: File '{idl_file}' does not exist[/red]")
            raise typer.Exit(1)

        # Read IDL file
        logger.debug(f"Reading IDL file: {idl_file}")
        content = idl_file.read_text()

        # Parse
        parser = IDLParser()
        ast = parser.parse(content)

        # Validate
        validator = SemanticValidator()
        errors = validator.validate(ast)

        if errors:
            console.print("[red]Validation errors:[/red]")
            for error in errors:
                console.print(f"  [yellow]•[/yellow] {error}")
            raise typer.Exit(1)

        # Output
        if json:
            json_data = ast.model_dump(mode="json", exclude_none=True)
            json_str = json_lib.dumps(json_data, indent=2)
            
            if output:
                output.write_text(json_str)
                console.print(f"[green]✓[/green] AST written to {output}")
            else:
                console.print(json_str)
        else:
            # Display summary
            console.print(f"[green]✓[/green] Successfully parsed {idl_file}")
            
            table = Table(title="IDL File Summary")
            table.add_column("Namespace", style="cyan")
            table.add_column("Interfaces", justify="right")
            table.add_column("Enums", justify="right")
            table.add_column("Typedefs", justify="right")
            table.add_column("Constants", justify="right")
            
            for ns in ast.namespaces:
                table.add_row(
                    ns.name,
                    str(len(ns.interfaces)),
                    str(len(ns.enums)),
                    str(len(ns.typedefs)),
                    str(len(ns.constants)),
                )
            
            console.print(table)

    except Exception as e:
        logger.exception("Failed to parse IDL file")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def generate(
    idl_file: Annotated[
        Optional[Path],
        typer.Argument(help="IDL file to compile (or use --from-ast)"),
    ] = None,
    target: Annotated[
        str,
        typer.Option(
            "-t",
            "--target",
            help="Target language/format (cpp, c, swift, all)",
        ),
    ] = "cpp",
    output_dir: Annotated[
        Path, typer.Option("-o", "--output", help="Output directory")
    ] = Path("."),
    from_ast: Annotated[
        Optional[Path],
        typer.Option("--from-ast", help="Load AST from JSON file instead of parsing IDL"),
    ] = None,
    cache_ast: Annotated[
        bool,
        typer.Option("--cache-ast", help="Save AST to file for later use"),
    ] = False,
    ast_file: Annotated[
        Optional[Path],
        typer.Option("--ast-file", help="AST cache file path"),
    ] = None,
    enum_class: Annotated[
        bool,
        typer.Option("--enum-class", help="Use enum class for C++ generation"),
    ] = False,
    template_dir: Annotated[
        Optional[Path],
        typer.Option("--templates", help="Custom template directory"),
    ] = None,
    project: Annotated[
        bool,
        typer.Option("--project", help="Generate complete project structure"),
    ] = True,
) -> None:
    """Generate code from an IDL file.
    
    Examples:
        minimidl generate myapi.idl --target cpp
        minimidl generate myapi.idl --target all --output ./generated
        minimidl generate --from-ast myapi.ast --target swift
    """
    try:
        # Validate inputs
        if not from_ast and not idl_file:
            console.print("[red]Error: Either provide an IDL file or use --from-ast[/red]")
            raise typer.Exit(1)

        if from_ast and idl_file:
            console.print("[red]Error: Cannot use both IDL file and --from-ast[/red]")
            raise typer.Exit(1)

        # Load or parse AST
        if from_ast:
            if not from_ast.exists():
                console.print(f"[red]Error: AST file '{from_ast}' does not exist[/red]")
                raise typer.Exit(1)
            
            logger.info(f"Loading AST from {from_ast}")
            ast = load_ast(from_ast)
        else:
            if not idl_file.exists():
                console.print(f"[red]Error: IDL file '{idl_file}' does not exist[/red]")
                raise typer.Exit(1)
            
            # Parse IDL file
            logger.info(f"Parsing {idl_file}")
            content = idl_file.read_text()
            parser = IDLParser()
            ast = parser.parse(content)

            # Cache AST if requested
            if cache_ast:
                ast_path = ast_file or idl_file.with_suffix(".ast")
                logger.info(f"Caching AST to {ast_path}")
                save_ast(ast, ast_path)
                console.print(f"[green]✓[/green] AST cached to {ast_path}")

        # Validate
        validator = SemanticValidator()
        errors = validator.validate(ast)

        if errors:
            console.print("[red]Validation errors:[/red]")
            for error in errors:
                console.print(f"  [yellow]•[/yellow] {error}")
            raise typer.Exit(1)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        config = {
            "enum_class": enum_class,
        }

        # Generate based on target
        targets = []
        if target == "all":
            targets = ["cpp", "c", "swift"]
        elif target in ["cpp", "c", "swift"]:
            targets = [target]
        else:
            console.print(f"[red]Error: Unknown target '{target}'[/red]")
            console.print("Valid targets: cpp, c, swift, all")
            raise typer.Exit(1)

        total_files = 0
        
        with console.status("[bold green]Generating code...[/bold green]") as status:
            for tgt in targets:
                status.update(f"[bold green]Generating {tgt.upper()} code...[/bold green]")
                
                if project and tgt in ["cpp", "swift"]:
                    # Use workflow for complete project
                    generated_files = _generate_with_workflow(
                        ast, tgt, output_dir, config, template_dir
                    )
                else:
                    # Use direct generator
                    generated_files = _generate_direct(
                        ast, tgt, output_dir, config, template_dir
                    )
                
                total_files += len(generated_files)
                console.print(f"[green]✓[/green] Generated {len(generated_files)} {tgt.upper()} files")

        console.print(f"\n[bold green]Success![/bold green] Generated {total_files} files total")

    except Exception as e:
        logger.exception("Failed to generate code")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _generate_with_workflow(
    ast: IDLFile,
    target: str,
    output_dir: Path,
    config: dict,
    template_dir: Path | None,
) -> list[Path]:
    """Generate using workflow for complete project."""
    if target == "cpp":
        workflow = CppWorkflow(config)
        return workflow.generate_project(ast, output_dir)
    elif target == "swift":
        workflow = SwiftWorkflow(config)
        return workflow.generate_project(ast, output_dir)
    else:
        return _generate_direct(ast, target, output_dir, config, template_dir)


def _generate_direct(
    ast: IDLFile,
    target: str,
    output_dir: Path,
    config: dict,
    template_dir: Path | None,
) -> list[Path]:
    """Generate using direct generator."""
    if target == "cpp":
        generator = CppGenerator(template_dir=template_dir)
    elif target == "c":
        generator = CWrapperGenerator(template_dir=template_dir)
    elif target == "swift":
        generator = SwiftGenerator(template_dir=template_dir)
    else:
        raise ValueError(f"Unknown target: {target}")
    
    return generator.generate(ast, output_dir)


@app.command()
def validate(
    idl_file: Annotated[Path, typer.Argument(help="IDL file to validate")],
) -> None:
    """Validate an IDL file without generating code."""
    try:
        # Validate file exists
        if not idl_file.exists():
            console.print(f"[red]Error: File '{idl_file}' does not exist[/red]")
            raise typer.Exit(1)

        # Read and parse
        logger.info(f"Validating {idl_file}")
        content = idl_file.read_text()
        parser = IDLParser()
        ast = parser.parse(content)

        # Validate
        validator = SemanticValidator()
        errors = validator.validate(ast)

        if errors:
            console.print(f"[red]✗[/red] Validation failed with {len(errors)} errors:")
            for error in errors:
                console.print(f"  [yellow]•[/yellow] {error}")
            raise typer.Exit(1)
        else:
            console.print(f"[green]✓[/green] {idl_file} is valid")

    except Exception as e:
        logger.exception("Validation failed")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()