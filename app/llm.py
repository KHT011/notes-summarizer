from __future__ import annotations

import json
import httpx

from .config import SETTINGS
from .prompt import SYSTEM_PROMPT, STRICT_APPENDIX, USER_PROMPT_TEMPLATE


class LLMError(RuntimeError):
    pass


def run_llm(raw_text: str, summary_mode: str, strict: bool = False, llm_provider: str | None = None) -> str:
    system_prompt = SYSTEM_PROMPT
    if strict:
        system_prompt = f"{SYSTEM_PROMPT}\n\n{STRICT_APPENDIX}"

    user_prompt = USER_PROMPT_TEMPLATE.format(raw_text=raw_text, summary_mode=summary_mode)
    provider = (llm_provider or SETTINGS.llm_provider).strip().lower()

    if provider == "ollama":
        return _run_ollama(system_prompt, user_prompt)
    if provider == "mistral":
        return _run_mistral(system_prompt, user_prompt)
    if provider == "openai":
        return _run_openai(system_prompt, user_prompt)

    raise LLMError(f"Unsupported LLM provider: {provider}")


def _run_mistral(system_prompt: str, user_prompt: str) -> str:
    if not SETTINGS.mistral_api_key:
        raise LLMError("MISTRAL_API_KEY is not set")

    payload = {
        "model": SETTINGS.mistral_model,
        "temperature": min(max(SETTINGS.temperature, 0.0), 0.2),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {"Authorization": f"Bearer {SETTINGS.mistral_api_key}"}
    url = f"{SETTINGS.mistral_base_url.rstrip('/')}/chat/completions"

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMError(f"Mistral request failed: {exc}") from exc

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise LLMError("Mistral response was not valid JSON") from exc

    choices = data.get("choices") or []
    if not choices:
        raise LLMError("Mistral response had no choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise LLMError("Mistral response had no content")

    return content.strip()


def _run_openai(system_prompt: str, user_prompt: str) -> str:
    if not SETTINGS.openai_api_key:
        raise LLMError("OPENAI_API_KEY is not set")

    payload = {
        "model": SETTINGS.openai_model,
        "temperature": min(max(SETTINGS.temperature, 0.0), 0.2),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {"Authorization": f"Bearer {SETTINGS.openai_api_key}"}
    url = f"{SETTINGS.openai_base_url.rstrip('/')}/chat/completions"

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMError(f"OpenAI request failed: {exc}") from exc

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise LLMError("OpenAI response was not valid JSON") from exc

    choices = data.get("choices") or []
    if not choices:
        raise LLMError("OpenAI response had no choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise LLMError("OpenAI response had no content")

    return content.strip()


def _run_ollama(system_prompt: str, user_prompt: str) -> str:
    try:
        import ollama
    except Exception as exc:
        raise LLMError("ollama package is not installed") from exc

    try:
        client = ollama.Client(host=SETTINGS.ollama_host)
        response = client.chat(
            model=SETTINGS.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": min(max(SETTINGS.temperature, 0.0), 0.2)},
        )
    except Exception as exc:
        raise LLMError(f"Ollama request failed: {exc}") from exc

    message = (response or {}).get("message") or {}
    content = message.get("content")
    if not content:
        raise LLMError("Ollama response had no content")

    return content.strip()
