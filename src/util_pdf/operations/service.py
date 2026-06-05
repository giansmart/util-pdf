"""UI-agnostic service layer.

Frontends (CLI, interactive shell, future desktop GUI) call into here. Each
function validates its input, raises a typed :class:`UtilPdfError` on failure,
and returns a small result object on success. No printing, no ``sys.exit`` —
the frontend decides how to surface outcomes.
"""

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from util_pdf.operations.convert import WORD_EXTENSIONS, convert_to_pdf
from util_pdf.operations.errors import ValidationError
from util_pdf.operations.merge import SUPPORTED_EXTENSIONS, merge_documents
from util_pdf.operations.remove_pages import parse_page_ranges
from util_pdf.operations.remove_pages import remove_pages as _remove_pages

DEFAULT_MERGE_OUTPUT = Path("merged.pdf")


@dataclass
class MergeResult:
    output: Path
    pages: int


@dataclass
class ConvertResult:
    output: Path


@dataclass
class RemovePagesResult:
    output: Path
    pages_removed: int
    pages_remaining: int


def merge(files: list[Path], output: Path | None = None) -> MergeResult:
    """Validate and merge ``files`` into a single PDF at ``output``."""
    output = output or DEFAULT_MERGE_OUTPUT

    errors: list[str] = []
    if len(files) < 2:
        errors.append("At least 2 files are required.")
    errors.extend(f"File not found: {f}" for f in files if not f.exists())

    unsupported = [
        f for f in files
        if f.exists() and f.suffix.lower() not in SUPPORTED_EXTENSIONS
    ]
    errors.extend(f"Unsupported file type: {f}" for f in unsupported)

    if errors:
        hint = "Supported: .pdf, .docx, .doc" if unsupported else None
        raise ValidationError(errors, hint=hint)

    pages = merge_documents(files, output)
    return MergeResult(output=output, pages=pages)


def convert(file: Path, output: Path | None = None) -> ConvertResult:
    """Validate and convert a Word document ``file`` to PDF."""
    if not file.exists():
        raise ValidationError(f"File not found: {file}")
    if file.suffix.lower() not in WORD_EXTENSIONS:
        raise ValidationError(
            f"Not a Word document: {file}", hint="Supported: .docx, .doc"
        )

    out_path = output or file.with_suffix(".pdf")

    with tempfile.TemporaryDirectory() as tmp:
        produced = convert_to_pdf(file, Path(tmp))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(produced), str(out_path))

    return ConvertResult(output=out_path)


def remove_pages(file: Path, pages_spec: str, output: Path | None = None) -> RemovePagesResult:
    """Validate and remove pages from *file*, writing the result to *output*."""
    from pypdf import PdfReader

    if not file.exists():
        raise ValidationError(f"File not found: {file}")
    if file.suffix.lower() != ".pdf":
        raise ValidationError(f"Not a PDF file: {file}", hint="Only PDF files are supported.")

    total = len(PdfReader(file).pages)
    if total == 0:
        raise ValidationError("The PDF has no pages.")

    try:
        indices = parse_page_ranges(pages_spec, total)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    if not indices:
        raise ValidationError("No pages specified.")
    if len(indices) >= total:
        raise ValidationError(
            f"Cannot remove all {total} pages — at least one page must remain."
        )

    out_path = output or file.with_stem(file.stem + "-edited")
    remaining = _remove_pages(file, indices, out_path)
    return RemovePagesResult(
        output=out_path,
        pages_removed=len(indices),
        pages_remaining=remaining,
    )
