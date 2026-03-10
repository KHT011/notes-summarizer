from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from .config import SETTINGS
from .schema import NotesOutput

PENDING_NOTES: Dict[str, Dict[str, Any]] = {}


def create_pending(
    input_text: str,
    summary_mode: str,
    notes: NotesOutput,
    prompt_version: str,
    llm_provider: str | None = None,
) -> Dict[str, Any]:
    record = {
        "id": str(uuid4()),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "summary_mode": summary_mode,
        "llm_provider": llm_provider or SETTINGS.llm_provider,
        "input_text": input_text,
        "notes": notes.model_dump(),
        "pending": True,
    }
    PENDING_NOTES[record["id"]] = record
    return record


def save_notes(
    input_text: str,
    summary_mode: str,
    notes: NotesOutput,
    prompt_version: str,
    llm_provider: str | None = None,
    note_id: str | None = None,
    stored_at: str | None = None,
) -> Dict[str, Any]:
    record = {
        "id": note_id or str(uuid4()),
        "stored_at": stored_at or datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "summary_mode": summary_mode,
        "llm_provider": llm_provider or SETTINGS.llm_provider,
        "input_text": input_text,
        "notes": notes.model_dump(),
    }

    path = Path(SETTINGS.storage_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_notes(note_id: str) -> Optional[Dict[str, Any]]:
    path = Path(SETTINGS.storage_path)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("id") == note_id:
                return record
    return None


def get_pending(note_id: str) -> Optional[Dict[str, Any]]:
    return PENDING_NOTES.get(note_id)


def pop_pending(note_id: str) -> Optional[Dict[str, Any]]:
    return PENDING_NOTES.pop(note_id, None)
