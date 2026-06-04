from pathlib import Path

import pytest
from pypdf import PdfWriter

from util_pdf.operations import merge as merge_mod
from util_pdf.operations.convert import LibreOfficeNotFound, convert_to_pdf
from util_pdf.operations.merge import merge_documents


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)
    return path


def test_merge_documents_pdfs_only(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf", pages=1)
    b = make_pdf(tmp_path / "b.pdf", pages=2)
    output = tmp_path / "out.pdf"

    assert merge_documents([a, b], output) == 3
    assert output.exists()


def test_merge_documents_converts_word(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    a = make_pdf(tmp_path / "a.pdf", pages=1)
    word = tmp_path / "b.docx"
    word.write_text("not a real docx, conversion is mocked")

    def fake_convert(src: Path, out_dir: Path, timeout: int = 120) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        produced = out_dir / f"{src.stem}.pdf"
        return make_pdf(produced, pages=2)

    monkeypatch.setattr(merge_mod, "convert_to_pdf", fake_convert)
    output = tmp_path / "out.pdf"

    assert merge_documents([a, word], output) == 3
    assert output.exists()


def test_convert_raises_without_libreoffice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("util_pdf.operations.convert.find_soffice", lambda: None)

    with pytest.raises(LibreOfficeNotFound):
        convert_to_pdf(tmp_path / "x.docx", tmp_path / "out")
