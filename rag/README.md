# Nova AI - Chat With Your PDF

Upload a PDF and ask questions about it. The answers come from your PDF and show page numbers.

## How it works
PDF → small chunks → embeddings → FAISS store → AI finds the best 5 chunks → AI answers

## Files
| File | What it does |
|---|---|
| `backend.py` | Builds the chatbot for one PDF |
| `main.py` | FastAPI server (upload and chat routes) |
| `index.html` | The web page |
| `rag.ipynb` | The first notebook version |
| `uploads/` | Uploaded PDFs are saved here |

## Run it
```
uvicorn main:app --reload
```
Then open `http://localhost:8000`.

## Notes
- Only PDF files, up to 20 MB.
- Add `GROQ_API_KEY` to a `.env` file.
