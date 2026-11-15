import os
import shutil
import html
import tempfile
from pathlib import Path

import markdown
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

import crag as crag_module   # your CRAG logic

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Vercel only allows writing to the temp folder
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# turns **bold**, * lists, tables etc. into proper HTML
def render_md(text):
    safe = html.escape(text)
    return markdown.markdown(safe, extensions=["extra", "nl2br", "sane_lists"])


templates.env.filters["md"] = render_md

# simple in-memory state
state = {
    "pdf_name": None,
    "pdf_path": None,
    "messages": [],   # each: {"question", "answer", "source"}
    "error": None,
}


@app.get("/static/style.css")
def css():
    return FileResponse(BASE_DIR / "static" / "style.css", media_type="text/css")


@app.get("/")
def home(request: Request):
    error = state["error"]
    state["error"] = None

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "pdf_name": state["pdf_name"],
            "messages": state["messages"],
            "error": error,
        },
    )


@app.post("/upload")
def upload(pdf: UploadFile = File(...)):
    if not pdf.filename.lower().endswith(".pdf"):
        state["error"] = "Please upload a PDF file."
        return RedirectResponse("/", status_code=303)

    path = os.path.join(UPLOAD_DIR, pdf.filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    try:
        crag_module.build_index(path)
        state["pdf_name"] = pdf.filename
        state["pdf_path"] = path
        state["messages"] = []
        crag_module.chat_history.clear()
    except Exception as e:
        state["error"] = f"Could not read PDF: {e}"

    return RedirectResponse("/", status_code=303)


@app.post("/ask")
def ask(question: str = Form(...)):
    # serverless can restart: rebuild the index from the saved PDF if needed
    if crag_module.retriever is None and state["pdf_path"] and os.path.exists(state["pdf_path"]):
        crag_module.build_index(state["pdf_path"])

    if crag_module.retriever is None:
        state["error"] = "Upload a PDF first."
        return RedirectResponse("/", status_code=303)

    try:
        answer, source = crag_module.crag(question)
        state["messages"].append({
            "question": question,
            "answer": answer,
            "source": source,
        })
    except Exception as e:
        state["error"] = f"Error: {e}"

    return RedirectResponse("/", status_code=303)


@app.post("/clear")
def clear():
    state["messages"] = []
    crag_module.chat_history.clear()
    return RedirectResponse("/", status_code=303)
