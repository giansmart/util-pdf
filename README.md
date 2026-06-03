# util-pdf

Open-source PDF utilities. Merge, split, and convert PDF files from the command line.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
uv pip install -e .
```

## Commands

### merge

Merge multiple PDF files into a single PDF.

```bash
pdf merge file1.pdf file2.pdf file3.pdf
```

By default the output is saved as `merged.pdf` in the current directory. Use `-o` to specify a custom output path:

```bash
pdf merge file1.pdf file2.pdf -o output/result.pdf
```

You can also use shell glob patterns:

```bash
pdf merge *.pdf -o merged.pdf
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
