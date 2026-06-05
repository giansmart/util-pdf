import shlex
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from util_pdf.operations import service
from util_pdf.operations.errors import UtilPdfError

VERSION = "0.1.0"

console = Console()

UNICORN = """\
[red]              ▲[/red]
[orange1]              █[/orange1]
[yellow]              █[/yellow]
             [green]▟[/green][cyan]█[/cyan][blue]▙[/blue]
        [white]▄▄▄▄▟███▖[/white]   [hot_pink]▒▒▒[/hot_pink]
      [white]▟█████████▙[/white]  [hot_pink]▒▒▒▒▒[/hot_pink]
   [white]▄▟████[/white] [grey42]●[/grey42] [white]██████[/white][hot_pink]▒▒▒▒▒▒[/hot_pink]
  [white]▟███████████████[/white][hot_pink]▒▒▒▒▒[/hot_pink]
  [white]▜███▛▀▀   ▟██████[/white][deep_pink2]▒▒▒▒▒[/deep_pink2]
   [white]▀▀      ▟███████▙[/white][deep_pink2]▒▒▒▒[/deep_pink2]
          [white]▟████████▌[/white][deep_pink2]▒▒▒[/deep_pink2]
           [white]▜███████▌[/white][deep_pink2]▒▒[/deep_pink2]
            [white]▜▙▄▄▄▄▟▘[/white]
"""

SIDE_INFO = """\
[bold]Open-source PDF toolkit[/bold]
[dim]for your terminal.[/dim]

[cyan]merge[/cyan]          [dim]Merge PDFs / Word docs[/dim]
[cyan]convert[/cyan]        [dim]Word (.docx) to PDF[/dim]
[cyan]remove-pages[/cyan]   [dim]Remove pages from a PDF[/dim]
[cyan]help[/cyan]           [dim]Show all commands[/dim]
[cyan]exit[/cyan]           [dim]Quit[/dim]\
"""


def _banner() -> Panel:
    grid = Table.grid(padding=(0, 4))
    grid.add_column()
    grid.add_column(vertical="middle")
    grid.add_row(Text.from_markup(UNICORN.rstrip("\n")), Text.from_markup(SIDE_INFO))

    body = Group(
        grid,
        Text(""),
        Align.center(Text.from_markup(f"[bold]util-pdf[/bold] [dim]v{VERSION}[/dim]")),
    )
    return Panel(body, box=ROUNDED, border_style="grey37", padding=(1, 3))


HELP = """\
[bold]Commands:[/bold]
  [cyan]merge[/cyan] <file1> <file2> [...] [-o output.pdf]     Merge PDFs/Word docs into one PDF
  [cyan]convert[/cyan] <file.docx> [-o output.pdf]             Convert a Word doc to PDF
  [cyan]remove-pages[/cyan] <file.pdf> -p <pages> [-o out.pdf] Remove pages (e.g. -p 3,5-7)
  [cyan]help[/cyan]                                             Show this message
  [cyan]exit[/cyan]                                             Quit
"""


def _print_error(error: UtilPdfError) -> None:
    for message in error.messages:
        console.print(f"[red]Error:[/red] {message}")
    if error.hint:
        console.print(f"[dim]{error.hint}[/dim]")


def _parse_merge(args: list[str]) -> tuple[list[Path], Path]:
    output = Path("merged.pdf")
    files: list[Path] = []
    i = 0
    while i < len(args):
        if args[i] in ("-o", "--output"):
            i += 1
            output = Path(args[i])
        else:
            files.append(Path(args[i]))
        i += 1
    return files, output


def _cmd_merge(args: list[str]) -> None:
    if not args:
        console.print("[red]Usage:[/red] merge <file1> <file2> [...] [-o output.pdf]")
        return

    try:
        files, output = _parse_merge(args)
    except IndexError:
        console.print("[red]Error:[/red] Missing value for -o option.")
        return

    try:
        with console.status("Merging..."):
            result = service.merge(files, output)
    except UtilPdfError as e:
        _print_error(e)
        return

    console.print(f"[green]Done.[/green] {result.pages} pages → [bold]{result.output}[/bold]")


def _cmd_convert(args: list[str]) -> None:
    if not args:
        console.print("[red]Usage:[/red] convert <file.docx> [-o output.pdf]")
        return

    file: Path | None = None
    output: Path | None = None
    i = 0
    try:
        while i < len(args):
            if args[i] in ("-o", "--output"):
                i += 1
                output = Path(args[i])
            elif file is None:
                file = Path(args[i])
            else:
                console.print(f"[red]Error:[/red] Unexpected argument: {args[i]}")
                return
            i += 1
    except IndexError:
        console.print("[red]Error:[/red] Missing value for -o option.")
        return

    if file is None:
        console.print("[red]Usage:[/red] convert <file.docx> [-o output.pdf]")
        return

    try:
        with console.status("Converting..."):
            result = service.convert(file, output)
    except UtilPdfError as e:
        _print_error(e)
        return

    console.print(f"[green]Done.[/green] → [bold]{result.output}[/bold]")


def _cmd_remove_pages(args: list[str]) -> None:
    if not args:
        console.print("[red]Usage:[/red] remove-pages <file.pdf> -p <pages> [-o output.pdf]")
        return

    file: Path | None = None
    pages_spec: str | None = None
    output: Path | None = None
    i = 0
    try:
        while i < len(args):
            if args[i] in ("-p", "--pages"):
                i += 1
                pages_spec = args[i]
            elif args[i] in ("-o", "--output"):
                i += 1
                output = Path(args[i])
            elif file is None:
                file = Path(args[i])
            else:
                console.print(f"[red]Error:[/red] Unexpected argument: {args[i]}")
                return
            i += 1
    except IndexError:
        console.print(f"[red]Error:[/red] Missing value for {args[i - 1]} option.")
        return

    if file is None or pages_spec is None:
        console.print("[red]Usage:[/red] remove-pages <file.pdf> -p <pages> [-o output.pdf]")
        return

    try:
        with console.status("Removing pages..."):
            result = service.remove_pages(file, pages_spec, output)
    except UtilPdfError as e:
        _print_error(e)
        return

    console.print(
        f"[green]Done.[/green] Removed {result.pages_removed} page(s), "
        f"{result.pages_remaining} remaining → [bold]{result.output}[/bold]"
    )


COMMANDS = {
    "merge": _cmd_merge,
    "convert": _cmd_convert,
    "remove-pages": _cmd_remove_pages,
}


def start_shell() -> None:
    console.print(_banner())
    console.print()

    session: PromptSession[str] = PromptSession(history=InMemoryHistory())

    while True:
        try:
            line = session.prompt("pdf > ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Bye![/dim]")
            break

        if not line:
            continue
        if line in ("exit", "quit", "q"):
            console.print("[dim]Bye![/dim]")
            break
        if line in ("help", "h", "?"):
            console.print(HELP)
            continue

        try:
            parts = shlex.split(line)
        except ValueError as e:
            console.print(f"[red]Parse error:[/red] {e}")
            continue

        cmd, *args = parts
        if cmd in COMMANDS:
            COMMANDS[cmd](args)
        else:
            console.print(f"[red]Unknown command:[/red] {cmd}. Type 'help' for available commands.")
