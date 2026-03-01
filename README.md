# AI Notes + Summary

Production-oriented implementation of a deterministic notes and summary pipeline with strict schema validation and export support.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure `.env`

Copy `.env.example` to `.env` and set values for the provider you want.

```text
# one of: mistral | openai | ollama
LLM_PROVIDER=mistral

# shared
LLM_TEMPERATURE=0.2
NOTES_STORAGE_PATH=data/notes.jsonl

# mistral
MISTRAL_API_KEY=your-mistral-key
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MISTRAL_MODEL=mistral-small-latest

# openai
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini

# ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Run

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## UI

The form includes an `LLM Provider` dropdown. That selection is used per request and overrides the default `LLM_PROVIDER` from `.env` for that single submission.

## API

`POST /process`

```json
{
  "text": "string",
  "summary_mode": "short | detailed | bullet",
  "llm_provider": "mistral | openai | ollama"
}
```

`llm_provider` is optional. If omitted, the app uses `.env` default `LLM_PROVIDER`.

Response:

```json
{
  "notes": {
    "title": "string | null",
    "key_points": ["..."] | null,
    "action_items": ["..."] | null,
    "definitions": ["..."] | null,
    "examples": ["..."] | null,
    "summary": "string | null"
  }
}
```

Response headers include `X-Notes-Id` and `X-Notes-Stored-At`.

## PDF Export

Install optional PDF dependencies:

```powershell
pip install -r requirements-pdf.txt
```

Export endpoints:
- `GET /export/markdown/{note_id}`
- `GET /export/pdf/{note_id}`

If PDF dependencies are missing, `/export/pdf/{note_id}` returns `501`.
