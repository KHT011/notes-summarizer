from __future__ import annotations

from .config import SETTINGS
from .llm import LLMError, run_llm
from .notes import ParseError, normalize_notes, parse_llm_output
from .schema import NotesOutput
from .storage import save_notes


class ValidationError(RuntimeError):
    pass


def preprocess(text: str) -> str:
    if text is None:
        return ""
    cleaned = text.strip().replace("\r\n", "\n").replace("\r", "\n")
    return cleaned


def validate_notes(notes: NotesOutput) -> NotesOutput:
    notes = normalize_notes(notes)
    # Ensure no empty lists remain
    for field in ("key_points", "action_items", "definitions", "examples"):
        values = getattr(notes, field)
        if values is not None and len(values) == 0:
            raise ValidationError(f"{field} must be None or non-empty")
    return notes


def process_notes(input_text: str, summary_mode: str, llm_provider: str | None = None) -> tuple[NotesOutput, dict]:
    cleaned = preprocess(input_text)

    if not cleaned:
        notes = NotesOutput(
            title=None,
            key_points=None,
            action_items=None,
            definitions=None,
            examples=None,
            summary=None,
        )
        record = save_notes(cleaned, summary_mode, notes, SETTINGS.prompt_version, llm_provider)
        return notes, record

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            llm_output = run_llm(cleaned, summary_mode, strict=attempt > 0, llm_provider=llm_provider)
            notes = parse_llm_output(llm_output)
            notes = validate_notes(notes)
            record = save_notes(cleaned, summary_mode, notes, SETTINGS.prompt_version, llm_provider)
            return notes, record
        except (LLMError, ParseError, ValidationError) as exc:
            last_error = exc
            continue

    raise ValidationError(f"Failed to produce valid output: {last_error}")
