from __future__ import annotations

from typing import Optional

from markdown import markdown as md_to_html

from .notes import render_markdown
from .schema import NotesOutput


class PdfExportUnavailable(RuntimeError):
    pass


def export_markdown(notes: NotesOutput) -> str:
    return render_markdown(notes)


def export_pdf(notes: NotesOutput) -> bytes:
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise PdfExportUnavailable("weasyprint is not installed or failed to import") from exc

    markdown_text = render_markdown(notes)
    html = md_to_html(markdown_text)
    return HTML(string=html).write_pdf()
