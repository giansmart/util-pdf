from pathlib import Path

import pytest
from pypdf import PdfWriter

from util_pdf.operations import convert as convert_mod
from util_pdf.operations import service
from util_pdf.operations.errors import ValidationError


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)
    return path


def test_merge_returns_result(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf", pages=1)
    b = make_pdf(tmp_path / "b.pdf", pages=2)
    output = tmp_path / "out.pdf"

    result = service.merge([a, b], output)

    assert result.output == output
    assert result.pages == 3
    assert output.exists()


def test_merge_requires_two_files(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf")

    with pytest.raises(ValidationError) as exc:
        service.merge([a], tmp_path / "out.pdf")

    assert any("At least 2 files" in m for m in exc.value.messages)


def test_merge_collects_all_validation_errors(tmp_path: Path) -> None:
    a = make_pdf(tmp_path / "a.pdf")
    missing = tmp_path / "missing.pdf"
    bad = tmp_path / "note.txt"
    bad.write_text("nope")

    with pytest.raises(ValidationError) as exc:
        service.merge([a, missing, bad], tmp_path / "out.pdf")

    messages = exc.value.messages
    assert any("File not found" in m for m in messages)
    assert any("Unsupported file type" in m for m in messages)
    assert exc.value.hint is not None


def test_convert_rejects_non_word(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "a.pdf")

    with pytest.raises(ValidationError) as exc:
        service.convert(pdf)

    assert any("Not a Word document" in m for m in exc.value.messages)


def test_convert_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValidationError) as exc:
        service.convert(tmp_path / "ghost.docx")

    assert any("File not found" in m for m in exc.value.messages)


def test_convert_invokes_libreoffice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    word = tmp_path / "doc.docx"
    word.write_text("mocked")

    def fake_convert(src: Path, out_dir: Path, timeout: int = 120) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        return make_pdf(out_dir / f"{src.stem}.pdf")

    monkeypatch.setattr(convert_mod, "convert_to_pdf", fake_convert)
    monkeypatch.setattr(service, "convert_to_pdf", fake_convert)
    output = tmp_path / "out.pdf"

    result = service.convert(word, output)

    assert result.output == output
    assert output.exists()
