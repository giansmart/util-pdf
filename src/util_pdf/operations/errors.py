"""Typed errors shared by every frontend (CLI, shell, future GUI).

Each error carries one or more human-readable ``messages`` plus an optional
``hint``, so a frontend can decide how to render them (colors, dialogs, JSON)
without the operations layer knowing anything about the UI.
"""

from collections.abc import Iterable


class UtilPdfError(Exception):
    """Base class for errors meant to be shown to the user."""

    def __init__(self, messages: str | Iterable[str], hint: str | None = None) -> None:
        if isinstance(messages, str):
            messages = [messages]
        self.messages: list[str] = list(messages)
        self.hint = hint
        super().__init__("\n".join(self.messages))


class ValidationError(UtilPdfError):
    """Raised when user input fails validation (missing files, bad types, ...)."""


class ConversionError(UtilPdfError):
    """Raised when a document cannot be converted to PDF."""


class LibreOfficeNotFound(ConversionError):
    """Raised when the LibreOffice binary cannot be located."""

    def __init__(self) -> None:
        super().__init__(
            "LibreOffice is required to convert Word documents but was not found.",
            hint=(
                "Install it from https://www.libreoffice.org/download/ "
                "(macOS: 'brew install --cask libreoffice')."
            ),
        )
