# AI Notes Summary

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063)
![Providers](https://img.shields.io/badge/LLM%20Providers-Ollama%20%7C%20Mistral%20%7C%20OpenAI-111827)
![Storage](https://img.shields.io/badge/Storage-JSONL-4B5563)

A modern FastAPI app that turns raw notes into structured, exportable summaries using your choice of LLM provider.

It supports:
- Web UI for quick note processing
- JSON API for programmatic workflows
- Multi-provider inference (Ollama, Mistral, OpenAI)
- Export to Markdown and PDF
- JSONL storage on export with stable note IDs

## Overview

AI Notes Summary takes unstructured text and normalizes it into a fixed schema:

- Title
- Key Points
- Action Items
- Definitions
- Examples
- Summary

The app is deterministic by design:
- It enforces strict section headers in prompt instructions.
- It retries once with stricter formatting rules when output is invalid.
- It normalizes empty values to `None` and validates list fields.

## Tech Stack

- Python 3.10+
- FastAPI + Uvicorn
- Pydantic v2
- Jinja2 templates
- httpx for provider APIs
- Ollama SDK (local models)
- WeasyPrint (PDF export)

## Project Structure

```text
app/
	main.py       # FastAPI routes + HTML/JSON responses
	core.py       # preprocess, validate, retry orchestration
	llm.py        # provider adapters (ollama/mistral/openai)
	notes.py      # markdown parsing + output rendering
	exporter.py   # markdown + PDF export
	storage.py    # JSONL persistence
	schema.py     # Pydantic request/response models
	prompt.py     # system/user prompt templates
data/
	notes.jsonl   # append-only note records
templates/
	index.html    # input form
	result.html   # rendered output + export links
static/
	styles.css
```

## Quick Start

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/KHT011/notes-summarizer.git
cd notes-summarizer
```


### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Set your provider and credentials in `.env`.

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Open:
- `http://127.0.0.1:8000` for the web app
- `http://127.0.0.1:8000/docs` for interactive API docs

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | Active provider: `ollama`, `mistral`, `openai` | `ollama` |
| `MISTRAL_API_KEY` | API key for Mistral | `None` |
| `MISTRAL_BASE_URL` | Mistral API base URL | `https://api.mistral.ai/v1` |
| `MISTRAL_MODEL` | Mistral chat model | `mistral-small-latest` |
| `OPENAI_API_KEY` | API key for OpenAI-compatible endpoint | `None` |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI chat model | `gpt-4.1-mini` |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Local Ollama model | `llama3.2` |
| `LLM_TEMPERATURE` | Clamped between 0.0 and 0.2 | `0.2` |
| `NOTES_STORAGE_PATH` | JSONL output path | `data/notes.jsonl` |

## Usage

### Web Flow

1. Open the home page.
2. Paste notes.
3. Choose provider + summary mode (`short`, `detailed`, `bullet`).
4. Submit and review structured output.
5. Export Markdown or PDF to persist the note.

### API Flow

#### POST `/process`

Request:

```json
{
	"text": "Today we discussed migration tasks, owner assignments, and launch risks.",
	"summary_mode": "short",
	"llm_provider": "mistral"
}
```

Response:

```json
{
	"notes": {
		"title": "Migration planning",
		"key_points": [
			"..."
		],
		"action_items": [
			"..."
		],
		"definitions": null,
		"examples": null,
		"summary": "..."
	}
}
```

Response headers include:
- `X-Notes-Id`
- `X-Notes-Stored-At`

#### GET `/export/markdown/{note_id}`

Returns markdown for the note and persists it if needed.

#### GET `/export/pdf/{note_id}`

Returns PDF bytes for the note and persists it if needed. If PDF backend is unavailable, returns `501`.

## Validation and Reliability

- Input is normalized (line ending cleanup + trim).
- Empty input returns a valid schema with all fields `None`.
- LLM output must contain all required sections.
- Parsing/validation errors trigger one strict retry.
- Failed generation returns `422` with an error message.

## Data Storage

Notes are written to `data/notes.jsonl` only when a user downloads Markdown or PDF. Pending notes are stored in memory and are lost if the server restarts.

Each stored note includes:
- UUID note ID
- UTC timestamp
- prompt version
- summary mode
- provider used
- original input
- normalized notes payload

## Provider Notes

- Ollama: best for local-first/private workflows.
- Mistral/OpenAI: require API keys and network access.
- Provider can be set globally (`LLM_PROVIDER`) or per request (`llm_provider`).

## Troubleshooting

- `Unsupported LLM provider`: ensure provider is one of `ollama`, `mistral`, `openai`.
- `...API_KEY is not set`: set key in `.env`.
- PDF export `501`: install/repair WeasyPrint runtime dependencies.
- Empty or malformed output: try another provider/model or shorter input blocks.

