# AI Notes + Summary

Production-oriented implementation of the deterministic notes + summary system.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set your LLM credentials:

```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4.1-mini"
```

Run the server:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## PDF Export

PDF export uses WeasyPrint. Install it separately if you need it:

```powershell
pip install -r requirements-pdf.txt
```

If WeasyPrint is not installed, `/export/pdf/{note_id}` returns HTTP 501.

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
