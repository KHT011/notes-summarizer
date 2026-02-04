from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class NotesOutput(BaseModel):
    title: Optional[str] = None
    key_points: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    definitions: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    summary: Optional[str] = None


class ProcessRequest(BaseModel):
    text: str = Field(default="")
    summary_mode: str = Field(default="short")

    @field_validator("summary_mode")
    @classmethod
    def validate_summary_mode(cls, value: str) -> str:
        allowed = {"short", "detailed", "bullet"}
        if value not in allowed:
            raise ValueError("summary_mode must be short, detailed, or bullet")
        return value


class ProcessResponse(BaseModel):
    notes: NotesOutput
