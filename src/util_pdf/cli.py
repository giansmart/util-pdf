import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from util_pdf.operations.convert import (
    WORD_EXTENSIONS,
    ConversionError,
    convert_to_pdf,
)
from util_pdf.operations.merge import SUPPORTED_EXTENSIONS, merge_documents

app = typer.Typer(help="PDF utilities.", invoke_without_command=True)
console = Console()


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
    if len(files) < 2:
        console.print("[red]Error:[/red] At least 2 files are required.")
        raise typer.Exit(1)

    missing = [f for f in files if not f.exists()]
    if missing:
        for f in missing:
            console.print(f"[red]Error:[/red] File not found: {f}")
        raise typer.Exit(1)

    unsupported = [f for f in files if f.suffix.lower() not in SUPPORTED_EXTENSIONS]
    if unsupported:
        for f in unsupported:
            console.print(f"[red]Error:[/red] Unsupported file type: {f}")
        console.print("[dim]Supported: .pdf, .docx, .doc[/dim]")
        raise typer.Exit(1)

    try:
        with console.status("Merging..."):
            total_pages = merge_documents(files, output)
    except ConversionError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"[green]Done.[/green] {total_pages} pages → [bold]{output}[/bold]")


@app.command()
def convert(
    file: Annotated[Path, typer.Argument(help="Word document (.doc/.docx) to convert.")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output PDF file.")] = None,
) -> None:
    """Convert a Word document (.doc/.docx) to PDF."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    if file.suffix.lower() not in WORD_EXTENSIONS:
        console.print(f"[red]Error:[/red] Not a Word document: {file}")
        console.print("[dim]Supported: .docx, .doc[/dim]")
        raise typer.Exit(1)

    out_path = output or file.with_suffix(".pdf")

    try:
        with console.status("Converting..."):
            with tempfile.TemporaryDirectory() as tmp:
                produced = convert_to_pdf(file, Path(tmp))
                out_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(produced), str(out_path))
    except ConversionError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"[green]Done.[/green] → [bold]{out_path}[/bold]")
