# GenAI Practice and Projects

My learning lab for Generative AI. It starts with small chatbot tests, teaches LangChain step by step, and ends with real working apps (job email agent, PDF chatbot, video summarizer, database chatbot and more).

Built with **Python**, **LangChain**, **LangGraph** and the **Groq** API. Some lessons use **Ollama** to run small models on your own computer.

---

## What is inside

### Learning folders (notebooks)

| Folder | What you learn |
|---|---|
| `langchain_ex` | LangChain basics in 5 parts: load data → split → embeddings → vector store → LLM and RAG |
| `updated_langchain` | New LangChain features: agents, structured output, streaming, middleware |
| `basic_chatbot` | LangGraph lessons: memory, tools, human approval, multi-agent |
| `mcp` | Tools on separate MCP servers (math and weather) with a client agent |

### Apps and projects

| Folder | What it is | Built with |
|---|---|---|
| `applymate-ai` | Writes job application emails and sends them after you approve | Flask |
| `rag` | **Nova AI** - upload a PDF and chat with it | FastAPI |
| `video_assistant` | **Vidi AI** - YouTube link or video → summary, action items, chat | Streamlit |
| `website-chatbot` | Answers questions from a scrap-business website | FastAPI |
| `chat_with_db` | Ask a SQLite database questions in plain English | Streamlit |
| `cineSage` | Paste a movie paragraph, get clean JSON, save to database | Streamlit |
| `qa_chatbot` | Simple chat app (memory in RAM) | Streamlit |
| `qa_chatbot_databse` | Chat app with memory saved in SQLite | Streamlit |
| `screen_reader` | Floating "AI" button that explains your screen (Windows) | Tkinter |

### Approval-step agents (human in the loop)

| Folder | What it is |
|---|---|
| `human_in_the_loop_middleware` | Stock chatbot that asks yes/no before a (fake) purchase |
| `email_sending_agent` | Sends an email only after you say yes |
| `movie_ticket_booking` | Ticket booking agent with approval |
| `restaurant-booking-systems` | Table booking agent (SQLite) with approval |

`src/chatbot` is an empty starter package. Each folder also has its own small README.

---

## Key words in simple English

- **LLM** - the AI brain (models from Groq).
- **LangChain** - a toolbox to connect the LLM with prompts, tools and documents.
- **LangGraph** - build an AI app like a flow chart: steps (nodes) joined by arrows (edges), sharing a notebook (state).
- **Tool** - a Python function the AI is allowed to call.
- **Agent** - an LLM plus tools. It decides when to use a tool.
- **Memory / `thread_id`** - saves the chat. Same id = same chat.
- **Human in the loop** - the AI pauses and waits for your yes/no.
- **RAG** - the AI first searches your own documents, then answers from them.
- **Embeddings and vector store** - text turned into numbers and saved in a small database (FAISS or Chroma) so we can search by meaning.
- **MCP** - a standard way to keep tools on a separate server.
- **Ollama** - runs small AI models on your computer.

---

## Setup

1. Install Python 3.12.
2. Install packages:
   ```
   pip install -r requirements.txt
   ```
   (or use `uv sync`)
3. Create a `.env` file in the main folder:
   ```
   GROQ_API_KEY=your_key_here
   ```
4. Run what you want (see below).

### Other keys (only if needed)

| Key | Needed for |
|---|---|
| `TAVILY_API_KEY` | Web search in `basic_chatbot` |
| `LANGCHAIN_API_KEY` | LangSmith tracing and `website-chatbot` |
| `HF_TOKEN` | `website-chatbot` |
| `SARVAM_API_KEY` | Hindi videos in `video_assistant` |
| `SENDER_EMAIL`, `GMAIL_APP_PASSWORD` | Email notebooks |

For Gmail, use an **App Password** (not your normal password): https://myaccount.google.com/apppasswords

> Never upload your `.env` file. It is already in `.gitignore`.

---

## How to run

| Project | Command (inside its folder) |
|---|---|
| `applymate-ai` | `python main.py` → open `localhost:5000` |
| `rag`, `website-chatbot` | `uvicorn main:app --reload` |
| `video_assistant` | `streamlit run app.py` |
| `chat_with_db` | `python sqlite.py` once, then `streamlit run sqlite_backend.py` |
| `cineSage` | `streamlit run main.py` |
| `qa_chatbot` | `streamlit run frontend_resuming_chat.py` |
| `qa_chatbot_databse` | `streamlit run frontend.py` |
| `screen_reader` | `python screen_reader.py` |
| `mcp` | `python weather_server.py`, then `python client.py` in another terminal |
| Notebooks (`.ipynb`) | Open and run cell by cell |

---

## Good to know

- `video_assistant` needs **ffmpeg** installed.
- `screen_reader` works on **Windows** only.
- `chat_with_db` uses a Windows folder path. Change it to your own path.
- Database files (`*.db`) are not in the repo. The scripts create them.
- Stock buying, email notebooks in `basic_chatbot` and `updated_langchain` are practice only (not real).

---

## Suggested learning order

1. `langchain_ex` (parts 001 to 005)
2. `updated_langchain`
3. `basic_chatbot`
4. `rag`, then `cineSage` and `chat_with_db`
5. `movie_ticket_booking`, `restaurant-booking-systems`, `email_sending_agent`
6. `mcp`
7. Full projects: `applymate-ai`, `video_assistant`, `website-chatbot`, `screen_reader`

---

## Author

GitHub: [@azrapatvi](https://github.com/azrapatvi)
