import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from util_pdf.operations.errors import ConversionError, LibreOfficeNotFound

# Re-exported so existing imports (``from ...convert import ConversionError``)
# keep working; the canonical definitions live in errors.py.
__all__ = [
    "WORD_EXTENSIONS",
    "ConversionError",
    "LibreOfficeNotFound",
    "find_soffice",
    "convert_to_pdf",
]

WORD_EXTENSIONS = {".doc", ".docx"}

# Set this to point at a custom LibreOffice install without touching the code.
_SOFFICE_ENV_VAR = "UTIL_PDF_SOFFICE"

# Well-known install locations, checked only after a PATH lookup fails. On Linux
# the binary is normally on PATH; macOS app bundles and Windows installers
# usually are not, hence these per-platform fallbacks.
_FALLBACK_PATHS = {
    "darwin": ["/Applications/LibreOffice.app/Contents/MacOS/soffice"],
    "win32": [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ],
}


def find_soffice() -> str | None:
    """Locate the LibreOffice binary, or return None if unavailable.

    Resolution order:
      1. The ``UTIL_PDF_SOFFICE`` environment variable, if it points to a file.
      2. ``soffice`` / ``libreoffice`` on ``PATH``.
      3. Well-known install locations for the current platform.
    """
    override = os.environ.get(_SOFFICE_ENV_VAR)
    if override:
        return override if Path(override).exists() else None

    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path

    for candidate in _FALLBACK_PATHS.get(sys.platform, []):
        if Path(candidate).exists():
            return candidate

    return None


def convert_to_pdf(src: Path, out_dir: Path, timeout: int = 120) -> Path:
    """Convert a .doc/.docx file to PDF inside out_dir, returning the new PDF path."""
    soffice = find_soffice()
    if soffice is None:
        raise LibreOfficeNotFound()

    out_dir.mkdir(parents=True, exist_ok=True)

    # Use an isolated user profile so conversion works even if a regular
    # LibreOffice instance is already running (otherwise it silently no-ops).
    with tempfile.TemporaryDirectory() as profile:
        profile_uri = Path(profile).as_uri()
        try:
            result = subprocess.run(
                [
                    soffice,
                    "--headless",
                    f"-env:UserInstallation={profile_uri}",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(out_dir),
                    str(src),
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise ConversionError(f"Conversion of {src.name} timed out.") from exc

    if result.returncode != 0:
        raise ConversionError(
            f"LibreOffice failed to convert {src.name}.\n{result.stderr.strip()}"
        )

    produced = out_dir / f"{src.stem}.pdf"
    if not produced.exists():
        raise ConversionError(f"LibreOffice did not produce a PDF for {src.name}.")
    return produced
