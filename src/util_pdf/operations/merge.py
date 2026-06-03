from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_pdfs(inputs: list[Path], output: Path) -> int:
    """Merge multiple PDFs into one. Returns total page count."""
    writer = PdfWriter()

    for path in inputs:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)

    return len(writer.pages)
