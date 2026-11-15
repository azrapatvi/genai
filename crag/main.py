import os
import shutil
import html

import markdown
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import crag as crag_module   # your CRAG logic

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# turns **bold**, * lists, tables etc. into proper HTML
def render_md(text):
    safe = html.escape(text)   # block any raw HTML for safety
    return markdown.markdown(safe, extensions=["extra", "nl2br", "sane_lists"])


templates.env.filters["md"] = render_md

os.makedirs("uploads", exist_ok=True)

# simple in-memory state (one user, local use)
state = {
    "pdf_name": None,
    "messages": [],   # each: {"question", "answer", "source"}
    "error": None,
}


@app.get("/")
def home(request: Request):
    error = state["error"]
    state["error"] = None   # show the error only once

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

    path = os.path.join("uploads", pdf.filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    try:
        crag_module.build_index(path)
        state["pdf_name"] = pdf.filename
        state["messages"] = []
        crag_module.chat_history.clear()
    except Exception as e:
        state["error"] = f"Could not read PDF: {e}"

    return RedirectResponse("/", status_code=303)


@app.post("/ask")
def ask(question: str = Form(...)):
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