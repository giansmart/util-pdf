import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from util_pdf.operations.convert import WORD_EXTENSIONS, convert_to_pdf

SUPPORTED_EXTENSIONS = {".pdf"} | WORD_EXTENSIONS


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


def merge_documents(inputs: list[Path], output: Path) -> int:
    """Merge PDFs and Word documents into a single PDF.

    Word documents (.doc/.docx) are converted to PDF on the fly before merging.
    Returns the total page count.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        pdf_inputs: list[Path] = []
        for index, path in enumerate(inputs):
            if path.suffix.lower() in WORD_EXTENSIONS:
                # A per-input subdir avoids collisions between same-named stems.
                pdf_inputs.append(convert_to_pdf(path, tmp_dir / str(index)))
            else:
                pdf_inputs.append(path)
        return merge_pdfs(pdf_inputs, output)
