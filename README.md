# util-pdf

<p align="center">
  <img src="assets/banner-util-pdf.jpg" alt="util-pdf" width="640">
</p>

A small, open-source command-line toolkit for working with PDFs — right from your terminal.

It currently supports **merging** PDFs and **converting Word documents (.doc/.docx) to PDF**, with an interactive shell mode. This is an early project — more operations (splitting, PDF → Word, and more) are planned for upcoming releases.

## Private by design

**Your files never leave your computer.** `util-pdf` runs entirely on your own machine — no servers, no uploads, no tracking.

Most online PDF tools require you to upload your documents to a website you don't control and whose data handling you can't verify. That's a real risk, especially for contracts, IDs, medical records, or anything sensitive. With `util-pdf`, that risk simply doesn't exist:

- **100% local** — every operation runs on your machine, offline.
- **No uploads** — your documents stay on disk and are never sent anywhere.
- **Open source** — the code is right here for you to read and audit.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [LibreOffice](https://www.libreoffice.org/download/) — only needed for Word → PDF conversion (the `convert` command, and merging Word docs). Not required for merging PDFs.
  - macOS: `brew install --cask libreoffice`
  - Debian/Ubuntu: `sudo apt install libreoffice`

> Conversion runs LibreOffice locally in headless mode — your documents are never uploaded anywhere.
>
> `util-pdf` finds LibreOffice on your `PATH` and in common install locations automatically. If yours lives elsewhere, point to it with the `UTIL_PDF_SOFFICE` environment variable.

## Installation

```bash
uv pip install -e .
```

This installs the `util-pdf` command.

## Usage

### Interactive mode

Run `util-pdf` with no arguments to start the interactive shell:

```bash
util-pdf
```

Inside the shell you can run commands directly (with command history via the arrow keys):

```
pdf > merge file1.pdf file2.pdf -o result.pdf
pdf > help
pdf > exit
```

### Direct commands

You can also run commands directly without entering the shell.

#### merge

Merge multiple PDF and/or Word files into a single PDF. Word documents are converted automatically, so you can mix formats freely:

```bash
util-pdf merge file1.pdf file2.docx file3.pdf -o joined.pdf
```

By default the output is saved as `merged.pdf` in the current directory. Use `-o` to specify a custom output path:

```bash
util-pdf merge file1.pdf file2.pdf -o output/result.pdf
```

You can also use shell glob patterns:

```bash
util-pdf merge *.pdf -o merged.pdf
```

**Options:**

| Option | Short | Description | Default |
|---|---|---|---|
| `--output` | `-o` | Output file path | `merged.pdf` |

#### convert

Convert a Word document (`.doc`/`.docx`) to PDF:

```bash
util-pdf convert report.docx
```

By default the PDF is saved next to the source file (same name, `.pdf` extension). Use `-o` to choose where it goes:

```bash
util-pdf convert report.docx -o out/report.pdf
```

**Options:**

| Option | Short | Description | Default |
|---|---|---|---|
| `--output` | `-o` | Output PDF path | `<source>.pdf` |

### Conversion fidelity

When converting Word documents, LibreOffice substitutes any fonts your system doesn't have. Because the substitutes have different metrics, the text can reflow slightly — and occasionally spill onto an extra blank page.

Installing free, metric-compatible versions of the common Microsoft fonts fixes this. It's a **one-time setup** that covers the large majority of documents (Calibri, Cambria, Arial and Times are Word's defaults), not something you do per file:

| Microsoft font | Metric-compatible replacement |
|---|---|
| Calibri / Cambria | Carlito / Caladea |
| Arial / Times New Roman / Courier New | Liberation Sans / Serif / Mono |

- macOS: `brew install --cask font-carlito font-caladea font-liberation`
- Debian/Ubuntu: `sudo apt install fonts-crosextra-carlito fonts-crosextra-caladea fonts-liberation`

If a specific document uses an unusual font, install that font as well.

## Development

Run tests:

```bash
uv run pytest tests/ -v
```

## License

See [LICENSE](LICENSE).
