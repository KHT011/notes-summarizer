from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import SETTINGS
from .core import ValidationError, process_notes
from .exporter import PdfExportUnavailable, export_markdown, export_pdf
from .schema import NotesOutput, ProcessRequest, ProcessResponse
from .storage import get_pending, load_notes, pop_pending, save_notes

app = FastAPI(title="AI Notes + Summary")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "default_llm_provider": SETTINGS.llm_provider,
        },
    )


@app.post("/process")
async def process(request: Request) -> Response:
    content_type = request.headers.get("content-type", "")
    accept = request.headers.get("accept", "")

    if "application/json" in content_type:
        payload = await request.json()
        data = ProcessRequest(**payload)
        notes, record = process_notes(data.text, data.summary_mode, data.llm_provider)
        response = ProcessResponse(notes=notes)
        headers = {
            "X-Notes-Id": record["id"],
            "X-Notes-Stored-At": record["stored_at"],
        }
        return JSONResponse(content=response.model_dump(), headers=headers)

    form = await request.form()
    text = str(form.get("text", ""))
    summary_mode = str(form.get("summary_mode", "short"))
    llm_provider = str(form.get("llm_provider", "")).strip() or None
    data = ProcessRequest(text=text, summary_mode=summary_mode, llm_provider=llm_provider)
    notes, record = process_notes(data.text, data.summary_mode, data.llm_provider)

    if "text/html" in accept or "application/json" not in accept:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "notes": notes,
                "note_id": record["id"],
            },
        )

    response = ProcessResponse(notes=notes)
    headers = {
        "X-Notes-Id": record["id"],
        "X-Notes-Stored-At": record["stored_at"],
    }
    return JSONResponse(content=response.model_dump(), headers=headers)


@app.get("/export/markdown/{note_id}")
def export_markdown_route(note_id: str) -> Response:
    record = load_notes(note_id)
    if not record:
        pending = get_pending(note_id)
        if not pending:
            raise HTTPException(status_code=404, detail="Note not found")
        notes = NotesOutput(**pending["notes"])
        save_notes(
            pending["input_text"],
            pending["summary_mode"],
            notes,
            pending["prompt_version"],
            pending.get("llm_provider"),
            note_id=pending["id"],
            stored_at=pending["stored_at"],
        )
        pop_pending(note_id)
    else:
        notes = NotesOutput(**record["notes"])

    markdown_text = export_markdown(notes)
    return PlainTextResponse(markdown_text, media_type="text/markdown")


@app.get("/export/pdf/{note_id}")
def export_pdf_route(note_id: str) -> Response:
    record = load_notes(note_id)
    if not record:
        pending = get_pending(note_id)
        if not pending:
            raise HTTPException(status_code=404, detail="Note not found")
        notes = NotesOutput(**pending["notes"])
        save_notes(
            pending["input_text"],
            pending["summary_mode"],
            notes,
            pending["prompt_version"],
            pending.get("llm_provider"),
            note_id=pending["id"],
            stored_at=pending["stored_at"],
        )
        pop_pending(note_id)
    else:
        notes = NotesOutput(**record["notes"])

    try:
        pdf_bytes = export_pdf(notes)
    except PdfExportUnavailable as exc:
        raise HTTPException(status_code=501, detail=str(exc))
    return Response(content=pdf_bytes, media_type="application/pdf")


@app.exception_handler(ValidationError)
def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": str(exc)})
