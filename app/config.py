from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    prompt_version: str = "v1"
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    storage_path: str = os.getenv("NOTES_STORAGE_PATH", "data/notes.jsonl")


SETTINGS = Settings()
