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

from util_pdf.operations.merge import merge_pdfs

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

[cyan]merge[/cyan]   [dim]Merge PDFs into one[/dim]
[cyan]help[/cyan]    [dim]Show all commands[/dim]
[cyan]exit[/cyan]    [dim]Quit[/dim]\
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
  [cyan]merge[/cyan] <file1.pdf> <file2.pdf> [...] [-o output.pdf]   Merge PDFs into one
  [cyan]help[/cyan]                                                   Show this message
  [cyan]exit[/cyan]                                                   Quit
"""


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
        console.print("[red]Usage:[/red] merge <file1.pdf> <file2.pdf> [...] [-o output.pdf]")
        return

    try:
        files, output = _parse_merge(args)
    except IndexError:
        console.print("[red]Error:[/red] Missing value for -o option.")
        return

    if len(files) < 2:
        console.print("[red]Error:[/red] At least 2 files required.")
        return

    missing = [f for f in files if not f.exists()]
    if missing:
        for f in missing:
            console.print(f"[red]Error:[/red] File not found: {f}")
        return

    non_pdf = [f for f in files if f.suffix.lower() != ".pdf"]
    if non_pdf:
        for f in non_pdf:
            console.print(f"[red]Error:[/red] Not a PDF: {f}")
        return

    total = merge_pdfs(files, output)
    console.print(f"[green]Done.[/green] {total} pages → [bold]{output}[/bold]")


COMMANDS = {
    "merge": _cmd_merge,
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
