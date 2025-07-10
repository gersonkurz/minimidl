"""MinimIDL command-line interface."""

from typing import Annotated

import typer

app = typer.Typer(
    name="minimidl",
    help="Modern Interface Definition Language compiler",
    add_completion=False,
)


@app.command()
def parse(
    idl_file: Annotated[str, typer.Argument(help="IDL file to parse")],
) -> None:
    """Parse an IDL file and display the AST."""
    typer.echo(f"Parsing {idl_file}...")
    typer.echo("Parser not yet implemented.")


def main() -> int:
    """Main entry point."""
    app()
    return 0


if __name__ == "__main__":
    main()
