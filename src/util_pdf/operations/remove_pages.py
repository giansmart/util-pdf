"""Remove specific pages from a PDF."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def parse_page_ranges(spec: str, total: int) -> list[int]:
    """Parse a page spec like '3,5-7,10' into a sorted list of 0-based indices.

    Pages are 1-based in user input; out-of-range numbers raise ValueError.
    """
    indices: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            raw_start, raw_end = part.split("-", 1)
            start = int(raw_start.strip())
            end = int(raw_end.strip())
            if start > end:
                raise ValueError(f"Invalid range {start}-{end}: start must be ≤ end.")
            for p in range(start, end + 1):
                if not (1 <= p <= total):
                    raise ValueError(f"Page {p} is out of range (PDF has {total} pages).")
                indices.add(p - 1)
        else:
            p = int(part)
            if not (1 <= p <= total):
                raise ValueError(f"Page {p} is out of range (PDF has {total} pages).")
            indices.add(p - 1)
    return sorted(indices)


def remove_pages(src: Path, pages_to_remove: list[int], output: Path) -> int:
    """Copy all pages of *src* except those at 0-based *pages_to_remove* into *output*.

    Returns the number of pages in the output PDF.
    """
    reader = PdfReader(src)
    writer = PdfWriter()
    remove_set = set(pages_to_remove)
    for i, page in enumerate(reader.pages):
        if i not in remove_set:
            writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)
    return len(writer.pages)
