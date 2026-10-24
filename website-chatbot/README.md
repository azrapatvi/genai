# Website Chatbot (Scrap Business)

A customer helper chatbot for a scrap business in Ratnagiri. It answers using the text from the business website.

## How it works
When the app starts, it reads 5 pages of the website, saves them in FAISS, and answers questions only from that text. If the answer is not there, it says so and suggests contacting the owner.

## Files
| File | What it does |
|---|---|
| `main.py` | FastAPI server with the `/chat` route |
| `templates/index.html` | The chat page |

## Run it
```
uvicorn main:app --reload
```
Then open `http://localhost:8000`.

## Notes
- Add `GROQ_API_KEY`, `HF_TOKEN` and `LANGCHAIN_API_KEY` to a `.env` file.
- You need internet, because the app reads the website at start-up.
