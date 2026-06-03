from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from util_pdf.operations.merge import merge_pdfs


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)
    return path


def test_merge_two_pdfs(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf", pages=2)
    b = make_pdf(tmp_path / "b.pdf", pages=3)
    output = tmp_path / "merged.pdf"

    total = merge_pdfs([a, b], output)

    assert total == 5
    assert output.exists()
    assert len(PdfReader(output).pages) == 5


def test_merge_preserves_order(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf", pages=1)
    b = make_pdf(tmp_path / "b.pdf", pages=1)
    c = make_pdf(tmp_path / "c.pdf", pages=1)
    output = tmp_path / "merged.pdf"

    total = merge_pdfs([a, b, c], output)

    assert total == 3


def test_merge_creates_output_dir(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf")
    b = make_pdf(tmp_path / "b.pdf")
    output = tmp_path / "subdir" / "out.pdf"

    merge_pdfs([a, b], output)

    assert output.exists()
