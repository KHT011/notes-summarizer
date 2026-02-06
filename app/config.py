from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    prompt_version: str = "v1"
    llm_provider: str = os.getenv("LLM_PROVIDER", "mistral")
    mistral_api_key: str | None = os.getenv("MISTRAL_API_KEY")
    mistral_base_url: str = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
    mistral_model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    storage_path: str = os.getenv("NOTES_STORAGE_PATH", "data/notes.jsonl")


SETTINGS = Settings()
