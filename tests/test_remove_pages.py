from pathlib import Path

import pytest
from pypdf import PdfWriter

from util_pdf.operations import service
from util_pdf.operations.errors import ValidationError
from util_pdf.operations.remove_pages import parse_page_ranges, remove_pages


def make_pdf(path: Path, pages: int = 5) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)
    return path


# --- parse_page_ranges ---

def test_parse_single_page() -> None:
    assert parse_page_ranges("3", 5) == [2]


def test_parse_range() -> None:
    assert parse_page_ranges("2-4", 5) == [1, 2, 3]


def test_parse_mixed() -> None:
    assert parse_page_ranges("1,3-4", 5) == [0, 2, 3]


def test_parse_out_of_range_raises() -> None:
    with pytest.raises(ValueError, match="out of range"):
        parse_page_ranges("6", 5)


def test_parse_invalid_range_raises() -> None:
    with pytest.raises(ValueError, match="start must be"):
        parse_page_ranges("4-2", 5)


# --- remove_pages (operation) ---

def test_removes_correct_pages(tmp_path: Path) -> None:
    src = make_pdf(tmp_path / "in.pdf", pages=5)
    out = tmp_path / "out.pdf"

    remaining = remove_pages(src, [1, 3], out)  # remove pages 2 and 4 (0-based)

    assert remaining == 3
    assert out.exists()


def test_creates_output_directory(tmp_path: Path) -> None:
    src = make_pdf(tmp_path / "in.pdf", pages=3)
    out = tmp_path / "sub" / "out.pdf"

    remove_pages(src, [0], out)

    assert out.exists()


# --- service.remove_pages ---

def test_service_remove_pages(tmp_path: Path) -> None:
    src = make_pdf(tmp_path / "in.pdf", pages=4)
    out = tmp_path / "out.pdf"

    result = service.remove_pages(src, "2,4", out)

    assert result.pages_removed == 2
    assert result.pages_remaining == 2
    assert result.output == out


def test_service_default_output_name(tmp_path: Path) -> None:
    src = make_pdf(tmp_path / "report.pdf", pages=3)

    result = service.remove_pages(src, "1")

    assert result.output.name == "report-edited.pdf"


def test_service_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="File not found"):
        service.remove_pages(tmp_path / "ghost.pdf", "1")


def test_service_rejects_non_pdf(tmp_path: Path) -> None:
    f = tmp_path / "doc.docx"
    f.write_text("nope")
    with pytest.raises(ValidationError, match="Not a PDF"):
        service.remove_pages(f, "1")


def test_service_rejects_removing_all_pages(tmp_path: Path) -> None:
    src = make_pdf(tmp_path / "in.pdf", pages=2)
    with pytest.raises(ValidationError, match="Cannot remove all"):
        service.remove_pages(src, "1-2")


def test_service_rejects_out_of_range_pages(tmp_path: Path) -> None:
    src = make_pdf(tmp_path / "in.pdf", pages=3)
    with pytest.raises(ValidationError, match="out of range"):
        service.remove_pages(src, "5")
