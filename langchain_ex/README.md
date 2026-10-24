# LangChain Basics (Step by Step)

A small course that teaches LangChain in 5 parts. Each part builds on the one before it.

**The big flow:** load data → split it → make embeddings → save in a vector store → ask the LLM

## Parts

| Folder | What you learn |
|---|---|
| `001_data_ingestion` | Load data from a text file, PDF, website and Wikipedia |
| `002_data_transformer` | Cut big text into small chunks (4 different splitters) |
| `003_Embeddings` | Turn text into numbers (HuggingFace and Ollama) |
| `004_vectore_store` | Save and search those numbers with FAISS and Chroma |
| `005_LLM` | Prompts, chat history, RAG, a LangServe API and an Ollama chatbot |

## Good to know
- Most files are Jupyter notebooks (`.ipynb`). Open them and run cell by cell.
- `speech.txt` is a short story used as sample text in the lessons.
- `faiss_index/` and `chroma_db/` are saved databases made by the notebooks. You do not need to read them.
- `005_LLM/serve.py` runs a small API: `python serve.py` (opens on `localhost:8000`, docs at `/docs`).
- `005_LLM/genai_app_with_ollama/main.py` is a chatbot that runs on your own computer: `streamlit run main.py` (Ollama must be installed).

## Setup
1. Install the packages: `pip install -r requirements.txt` (from the main folder).
2. Create a `.env` file with your `GROQ_API_KEY`.
