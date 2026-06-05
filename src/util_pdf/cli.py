from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from util_pdf.operations import service
from util_pdf.operations.errors import UtilPdfError

app = typer.Typer(help="PDF utilities.", invoke_without_command=True)
console = Console()


def _fail(error: UtilPdfError) -> None:
    """Render a typed error and abort with a non-zero exit code."""
    for message in error.messages:
        console.print(f"[red]Error:[/red] {message}")
    if error.hint:
        console.print(f"[dim]{error.hint}[/dim]")
    raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        from util_pdf.shell import start_shell
        start_shell()
        raise typer.Exit()


@app.command()
def merge(
    files: Annotated[list[Path], typer.Argument(help="PDF or Word files to merge (in order).")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output file.")] = Path("merged.pdf"),
) -> None:
    """Merge multiple PDF and/or Word (.doc/.docx) files into one PDF."""
    try:
        with console.status("Merging..."):
            result = service.merge(files, output)
    except UtilPdfError as e:
        _fail(e)

    console.print(f"[green]Done.[/green] {result.pages} pages → [bold]{result.output}[/bold]")


@app.command(name="remove-pages")
def remove_pages(
    file: Annotated[Path, typer.Argument(help="PDF file to edit.")],
    pages: Annotated[str, typer.Option("--pages", "-p", help="Pages to remove, e.g. '3,5-7'.")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output PDF file.")] = None,
) -> None:
    """Remove specific pages from a PDF.

    Pages are specified as 1-based numbers or ranges: -p 3,5-7,10
    """
    try:
        with console.status("Removing pages..."):
            result = service.remove_pages(file, pages, output)
    except UtilPdfError as e:
        _fail(e)

    console.print(
        f"[green]Done.[/green] Removed {result.pages_removed} page(s), "
        f"{result.pages_remaining} remaining → [bold]{result.output}[/bold]"
    )


@app.command()
def convert(
    file: Annotated[Path, typer.Argument(help="Word document (.doc/.docx) to convert.")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output PDF file.")] = None,
) -> None:
    """Convert a Word document (.doc/.docx) to PDF."""
    try:
        with console.status("Converting..."):
            result = service.convert(file, output)
    except UtilPdfError as e:
        _fail(e)

    console.print(f"[green]Done.[/green] → [bold]{result.output}[/bold]")
