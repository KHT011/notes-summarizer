# AI Notes + Summary

Production-oriented implementation of the deterministic notes + summary system.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure with .env

Create or update `.env` in the project root (see `.env.example`), then set:

```text
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your-key
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MISTRAL_MODEL=mistral-small-latest
LLM_TEMPERATURE=0.2

# Optional: Ollama fallback
# LLM_PROVIDER=ollama
# OLLAMA_HOST=http://localhost:11434
# OLLAMA_MODEL=llama3.2
```

Run the server:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## API

`POST /process`

```json
{
  "text": "string",
  "summary_mode": "short | detailed | bullet"
}
```

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

The response includes `X-Notes-Id` and `X-Notes-Stored-At` headers for exports.
