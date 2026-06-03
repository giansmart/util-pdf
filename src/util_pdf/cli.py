from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import track

from util_pdf.operations.merge import merge_pdfs

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
    files: Annotated[list[Path], typer.Argument(help="PDF files to merge (in order).")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output file.")] = Path("merged.pdf"),
) -> None:
    """Merge multiple PDF files into one."""
    if len(files) < 2:
        console.print("[red]Error:[/red] At least 2 files are required.")
        raise typer.Exit(1)

    missing = [f for f in files if not f.exists()]
    if missing:
        for f in missing:
            console.print(f"[red]Error:[/red] File not found: {f}")
        raise typer.Exit(1)

    non_pdf = [f for f in files if f.suffix.lower() != ".pdf"]
    if non_pdf:
        for f in non_pdf:
            console.print(f"[red]Error:[/red] Not a PDF: {f}")
        raise typer.Exit(1)

    for f in track(files, description="Merging..."):
        pass

    total_pages = merge_pdfs(files, output)
    console.print(f"[green]Done.[/green] {total_pages} pages → [bold]{output}[/bold]")
