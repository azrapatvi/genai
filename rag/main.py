
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend import create_pdf_graph
from langchain_core.messages import HumanMessage


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="PDF RAG Chatbot")

# Stores each uploaded PDF's graph in memory
sessions = {}


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    pdf_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"

    try:
        contents = await file.read()

        # Basic upload size limit: 20 MB
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="PDF must be smaller than 20 MB."
            )

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        # Save the PDF
        with open(pdf_path, "wb") as f:
            f.write(contents)

        # Build the RAG graph for this PDF
        graph = create_pdf_graph(str(pdf_path))

        # Give this conversation a unique ID
        session_id = str(uuid.uuid4())

        sessions[session_id] = {
            "graph": graph,
            "pdf_path": str(pdf_path),
            "filename": Path(file.filename).name
        }

        return {
            "message": "PDF uploaded successfully!",
            "session_id": session_id,
            "filename": Path(file.filename).name
        }

    except HTTPException:
        pdf_path.unlink(missing_ok=True)
        raise

    except Exception as e:
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Could not process PDF: {str(e)}"
        )

    finally:
        await file.close()


class ChatRequest(BaseModel):
    session_id: str
    question: str


@app.post("/chat")
async def chat(request: ChatRequest):
    session = sessions.get(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="PDF session not found. Please upload your PDF again."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    graph = session["graph"]

    try:
        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=request.question)
                ]
            },
            config={
                "configurable": {
                    "thread_id": request.session_id
                }
            }
        )

        # Get the last AI response, not a tool message
        answer = ""

        for message in reversed(result["messages"]):
            if message.type == "ai" and message.content:
                answer = message.content
                break

        return {
            "question": request.question,
            "answer": answer,
            "session_id": request.session_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )
