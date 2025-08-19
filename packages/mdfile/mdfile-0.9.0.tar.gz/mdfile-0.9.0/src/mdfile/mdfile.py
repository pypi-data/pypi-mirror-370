#!/user/bin/env -S uv run --script
# /// script
# dependencies = ["typer","rich"]
# ///
"""
MarkDown File Manipulation (MNM) - Tools for converting various file formats to Markdown.

This module provides functionality to convert different file types to Markdown format
for inclusion in documentation, reports, or Markdown-based websites. It supports a variety
of formats including CSV, JSON, code files with syntax highlighting, and plain text.

The intended interface is the command-line through Typer and more specifically to
be used with `uv run`. The main features include:

1. Automatic file format detection based on file extension
2. Conversion of CSV files to Markdown tables with customizable formatting
3. Pretty-printing and syntax highlighting for JSON and code files
4. Direct inclusion of existing Markdown files
5. Addition of file timestamps and other metadata
6. A file-reference system that can update Markdown files by replacing special comment tags

Key components:
- ToMarkdown: Abstract base class for all converters
- Various format-specific converter classes (CsvToMarkdown, JsonToMarkdown, etc.)
- markdown_factory: Factory function to create the appropriate converter
- Command-line interface for converting files or updating Markdown files with file references

NOTE: This module is SUPPOSED to be a single file so it is easy to use as a tool with uv.

Usage example:
    # Via CLI
    # python mdfile.py report.md --bold "Important,Critical"
"""
import pathlib
from importlib.metadata import version
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from typer import Typer

from .md_updater import update_markdown_file

__app_name__ = "mdfile"
__version__ = version(__app_name__)

def version_callback(value: bool):
    """Callback for typer."""
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

def handle_update_markdown_file(
        md_file: str,
        bold: str = '',
        auto_break: bool = False,
        out_file: str | None = None,
) -> str:
    """
    Wrapper for `update_markdown_file` that integrates with Typer for CLI interaction.

    Args:
        md_file (str): Path to the Markdown file to be read.
        bold (str, optional): String to be added in bold text format. Defaults to an empty string.
        auto_break (bool): If True, applies automatic line breaking within the content.
        out_file (str, optional): File to save the updated content. Defaults to overwriting
            the input file.

    Returns:
        None
    """
    try:
        updated_content = update_markdown_file(md_file,
                                               bold,
                                               auto_break,
                                               out_file
                                               )

        typer.echo(f"File '{md_file}' updated successfully.", err=True)
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)

    return updated_content


def version_callback(value:bool):
    """Show appp version"""
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

app = typer.Typer(add_completion=False)


@app.command()
def convert(
        file_name: str = typer.Argument( help="The file to convert to Markdown"),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file (if not specified, prints to stdout)"
        ),
        bold_values: Optional[str] = typer.Option(
            None, "--bold", "-b", help="Comma-separated values to make bold (for CSV files)"
        ),
        auto_break: Optional[bool] = typer.Option(
            True, "--auto-break/--no-auto-break", help="Disable automatic line breaks in CSV headers"
        ),
        plain: bool = typer.Option(
            False, "--plain", help="Output plain Markdown without rich formatting"
        ),
        version:bool= typer.Option(
            None, "--version", '-v' ,callback=version_callback, is_eager=True, help="Show version and exit"
        ),

):
    """Convert a file to Markdown based on its extension."""
    try:

        if not pathlib.Path(file_name).exists():
            typer.echo(f"Error: File '{file_name}' does not exist.", err=True)
            raise typer.Exit(code=1)

        markdown_text = handle_update_markdown_file(file_name,
                                                    bold=bold_values,
                                                    auto_break=auto_break)

        if output:
            with open(output, "w", encoding='utf8') as file:
                file.write(markdown_text)
            typer.echo(f"Markdown written to {output}", err=True)
        else:
            if markdown_text:
                if not plain:
                    # Use Rich to display formatted markdown
                    console = Console()
                    md = Markdown(markdown_text)
                    console.print(md)
                else:
                    # Output plain markdown
                    typer.echo(markdown_text)

            else:
                typer.echo("An Error Occurred", err=True)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
