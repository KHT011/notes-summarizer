from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .schema import NotesOutput

SECTION_ORDER = [
    "Title",
    "Key Points",
    "Action Items",
    "Definitions",
    "Examples",
    "Summary",
]

SECTION_KEYS = {
    "Title": "title",
    "Key Points": "key_points",
    "Action Items": "action_items",
    "Definitions": "definitions",
    "Examples": "examples",
    "Summary": "summary",
}


@dataclass(frozen=True)
class ParsedSections:
    sections: Dict[str, List[str]]


class ParseError(ValueError):
    pass


def _clean_scalar(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or cleaned.lower() == "none":
        return None
    return cleaned


def _clean_list(values: Optional[List[str]]) -> Optional[List[str]]:
    if not values:
        return None
    cleaned: List[str] = []
    for item in values:
        item_clean = item.strip()
        if not item_clean or item_clean.lower() == "none":
            continue
        cleaned.append(item_clean)
    if not cleaned:
        return None
    return cleaned


def normalize_notes(notes: NotesOutput) -> NotesOutput:
    return NotesOutput(
        title=_clean_scalar(notes.title),
        key_points=_clean_list(notes.key_points),
        action_items=_clean_list(notes.action_items),
        definitions=_clean_list(notes.definitions),
        examples=_clean_list(notes.examples),
        summary=_clean_scalar(notes.summary),
    )


def parse_llm_output(markdown_text: str) -> NotesOutput:
    sections = _split_sections(markdown_text)
    missing = [name for name in SECTION_ORDER if name not in sections]
    if missing:
        raise ParseError(f"Missing sections: {', '.join(missing)}")

    title_value = _clean_scalar(_first_or_none(sections["Title"]))
    summary_lines = sections["Summary"]
    summary_value = _clean_scalar("\n".join(summary_lines).strip())

    notes = NotesOutput(
        title=title_value,
        key_points=_clean_list(sections["Key Points"]),
        action_items=_clean_list(sections["Action Items"]),
        definitions=_clean_list(sections["Definitions"]),
        examples=_clean_list(sections["Examples"]),
        summary=summary_value,
    )
    return normalize_notes(notes)


def _split_sections(markdown_text: str) -> Dict[str, List[str]]:
    lines = [line.rstrip() for line in markdown_text.splitlines()]
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None

    for line in lines:
        if not line.strip():
            if current is not None:
                sections[current].append("")
            continue
        header = _match_header(line)
        if header:
            current = header
            sections[current] = []
            continue
        if current is None:
            continue
        if current == "Title":
            sections[current].append(line.strip())
            continue
        if line.lstrip().startswith("- ") or line.lstrip().startswith("* "):
            sections[current].append(line.lstrip()[2:].strip())
        else:
            sections[current].append(line.strip())

    return sections


def _match_header(line: str) -> Optional[str]:
    cleaned = line.strip()
    if cleaned.endswith(":"):
        cleaned = cleaned[:-1].strip()
    if cleaned.startswith("#"):
        cleaned = cleaned.lstrip("#").strip()
    for name in SECTION_KEYS:
        if cleaned.lower() == name.lower():
            return name
    return None


def _first_or_none(values: List[str]) -> Optional[str]:
    for value in values:
        if value.strip():
            return value
    return None


def render_markdown(notes: NotesOutput) -> str:
    lines: List[str] = []
    lines.append("## Title")
    lines.append(notes.title or "None")
    lines.append("")

    def render_list(label: str, values: Optional[List[str]]) -> None:
        lines.append(f"## {label}")
        if not values:
            lines.append("None")
            lines.append("")
            return
        for item in values:
            lines.append(f"- {item}")
        lines.append("")

    render_list("Key Points", notes.key_points)
    render_list("Action Items", notes.action_items)
    render_list("Definitions", notes.definitions)
    render_list("Examples", notes.examples)

    lines.append("## Summary")
    lines.append(notes.summary or "None")
    lines.append("")

    return "\n".join(lines).strip() + "\n"
