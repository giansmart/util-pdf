# util-pdf

<p align="center">
  <img src="assets/banner-util-pdf.jpg" alt="util-pdf" width="640">
</p>

A small, open-source command-line toolkit for working with PDFs — right from your terminal.

It currently supports **merging** PDF files, with an interactive shell mode. This is an early project — more document and PDF operations (splitting, Word ↔ PDF conversion, and more) are planned for upcoming releases.

## Private by design

**Your files never leave your computer.** `util-pdf` runs entirely on your own machine — no servers, no uploads, no tracking.

Most online PDF tools require you to upload your documents to a website you don't control and whose data handling you can't verify. That's a real risk, especially for contracts, IDs, medical records, or anything sensitive. With `util-pdf`, that risk simply doesn't exist:

- **100% local** — every operation runs on your machine, offline.
- **No uploads** — your documents stay on disk and are never sent anywhere.
- **Open source** — the code is right here for you to read and audit.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

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

Merge multiple PDF files into a single PDF:

```bash
util-pdf merge file1.pdf file2.pdf file3.pdf
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

## Development

Run tests:

```bash
uv run pytest tests/ -v
```

## License

See [LICENSE](LICENSE).
