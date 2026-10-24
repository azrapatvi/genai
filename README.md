# GenAI Practice and Projects

This repository is my **learning lab for Generative AI**. It starts with very small chatbot experiments, goes through the **LangChain basics step by step** (load data → split → embed → vector store → LLM → RAG → API), and grows into real working apps: a job-application email agent, a PDF chatbot, a video summarizer, a database chatbot, a screen reader and more.

Everything is built with **Python**, **LangChain**, **LangGraph** and the **Groq** API (mostly the `openai/gpt-oss-120b` model). Some lessons also use **Ollama** to run small models on your own computer.

---

## Table of Contents

1. [What is inside (quick view)](#1-what-is-inside-quick-view)
2. [Big ideas used in this repo (in simple words)](#2-big-ideas-used-in-this-repo-in-simple-words)
3. [Tech stack](#3-tech-stack)
4. [Folder structure](#4-folder-structure)
5. [Folder by folder explanation](#5-folder-by-folder-explanation)
6. [How to set up the project](#6-how-to-set-up-the-project)
7. [How to run each project](#7-how-to-run-each-project)
8. [Things to know before you run (known issues)](#8-things-to-know-before-you-run-known-issues)
9. [Suggested learning order](#9-suggested-learning-order)
10. [Author](#10-author)

---

## 1. What is inside (quick view)

| Folder | What it is | Type |
|---|---|---|
| `langchain_ex` | **LangChain basics course** in 5 numbered parts: data ingestion, text splitting, embeddings, vector stores (FAISS and Chroma), LLM / prompts / history / RAG / LangServe / Ollama | Notebooks + 2 scripts |
| `updated_langchain` | **Newer LangChain features**: agents, 3 ways of structured output, streaming and batch, summarization middleware, human-in-the-loop middleware | Notebooks |
| `basic_chatbot` | Step-by-step LangGraph lessons (memory, tools, human approval, multi-agent) | Notebooks + 1 script |
| `applymate-ai` | **ApplyMate AI** - writes job application emails and sends them after you approve | Flask web app |
| `rag` | **Nova AI** - upload a PDF and chat with it | FastAPI web app |
| `video_assistant` | **Vidi AI** - turn a YouTube link or video into summary, action items and a chat | Streamlit app |
| `website-chatbot` | Chatbot that answers questions from a scrap-business website | FastAPI web app |
| `chat_with_db` | Ask questions to a SQLite database in plain English | Streamlit app |
| `cineSage` | Paste a movie paragraph, get clean JSON, save it to a database | Streamlit app |
| `qa_chatbot` | Simple chat app with memory (in RAM) | Streamlit app |
| `qa_chatbot_databse` | Chat app whose memory is saved in a SQLite file | Streamlit app |
| `screen_reader` | Floating "AI" button that explains what is on your screen | Desktop app (Windows) |
| `mcp` | Math and weather tool servers using MCP, plus a client agent | Python scripts |
| `human_in_the_loop_middleware` | Pause the AI and ask a human before doing something important | Notebook + script |
| `email_sending_agent` | Send a real email only after you say "yes" | Notebook |
| `movie_ticket_booking` | Ticket booking agent with approval step | Notebook |
| `restaurant-booking-systems` | Table booking agent using SQLite and approval step | Notebook |
| `src/chatbot` | Empty starter package (just prints "Hello") | Python package |

---

## 2. Big ideas used in this repo (in simple words)

You will see these words again and again. Here is what they mean.

- **LLM** - The AI brain (here: models served by Groq).
- **LangChain** - A toolbox that helps connect the LLM to prompts, tools, documents and more.
- **LangGraph** - A way to build an AI app as a **flow chart**. Each box is a step, each arrow tells what comes next.
  - **State** - The shared notebook that every step can read and write (for example, the list of chat messages).
  - **Node** - One step in the flow (for example, "call the LLM").
  - **Edge** - An arrow between steps. A **conditional edge** chooses the next step based on a condition.
  - **`add_messages`** - A helper that keeps adding new messages to the chat list instead of replacing it.
- **Tool** - A normal Python function the AI is allowed to call (search the web, multiply numbers, book a table, send an email).
- **`ToolNode` and `tools_condition`** - Ready-made LangGraph parts. One runs the tool, the other decides "did the AI ask for a tool? then go to the tool, else finish".
- **Checkpointer (memory)** - Saves the state so the bot remembers earlier messages. `MemorySaver` / `InMemorySaver` keep it in RAM (lost when the app stops). `SqliteSaver` keeps it in a file (stays after restart).
- **`thread_id`** - The name of one conversation. Same id = same memory. New id = fresh chat.
- **Human-in-the-Loop (HITL)** - The AI pauses and waits for a human to say yes / no before a risky step. Done with `interrupt()` and resumed with `Command(resume=...)`, or with `HumanInTheLoopMiddleware`.
- **RAG (Retrieval Augmented Generation)** - Instead of letting the AI guess, we first **search our own documents** for the right pieces of text and give them to the AI so it answers from them.
  - **Chunking** - Cutting a long text into small pieces.
  - **Embeddings** - Turning text into numbers so we can find "similar meaning" text. We use `all-MiniLM-L6-v2`.
  - **Vector store** - A small database for those numbers (**FAISS** or **Chroma**).
- **MCP (Model Context Protocol)** - A standard way to put tools on a separate "server" so any AI client can use them.
- **Runnable / chain** - A LangChain pipeline written with `|` (for example `prompt | llm | parser`). `RunnableParallel` runs several chains at the same time.
- **Structured output** - Forcing the AI to reply in a fixed shape (JSON / Pydantic model). You can describe the shape with a **Pydantic class** (gives an object and checks the data), a **TypedDict** (gives a plain dictionary, no checking) or a **dataclass**.
- **Document and Loader** - A `Document` is a piece of text plus its `metadata` (like the source). A **loader** (`TextLoader`, `PyPDFLoader`, `WebBaseLoader`, `WikipediaLoader`) reads a file or website and returns Documents.
- **Text splitter** - Cuts big text into small chunks. `chunk_size` is how big each piece is, `chunk_overlap` is how much two neighbouring pieces share so no meaning is lost.
- **Prompt template and output parser** - A prompt template is a reusable message with blanks like `{language}`. A parser (`StrOutputParser`) turns the AI reply into plain text.
- **LCEL** - LangChain Expression Language: joining steps with `|`, for example `prompt | llm | parser`.
- **Retriever** - A vector store that can be asked "give me the chunks most like this question".
- **Chat history** - An LLM forgets everything after each call. To make it remember, you send the old messages again (`RunnableWithMessageHistory`), and you cut old messages with `trim_messages` so the history does not grow too big.
- **Agent** - An LLM **plus tools**. The LLM decides when to call a tool (for example a weather function) and then answers. Made with `create_agent`.
- **Middleware** - Extra code that sits around the agent. Examples here: **SummarizationMiddleware** (shortens a long chat automatically) and **HumanInTheLoopMiddleware** (asks a human before a risky tool runs).
- **Streaming and batch** - *Streaming* shows the answer little by little as it is written. *Batch* sends many questions together in one call.
- **LangServe** - Turns a LangChain chain into a web API (`/chain/invoke`, `/chain/batch`, `/chain/stream`) with FastAPI.
- **Ollama** - A program that runs small AI models **on your own computer** (no API key needed).

---

## 3. Tech stack

- **Language:** Python 3.12 (see `.python-version`)
- **AI frameworks:** LangChain, LangGraph, LangSmith (tracing)
- **LLM provider:** Groq (`openai/gpt-oss-120b` and `openai/gpt-oss-20b`; `qwen/qwen3.8-27b` for the screen reader because it needs vision)
- **Local models:** Ollama (`qwen2.5:0.5b` for chat, `nomic-embed-text` for embeddings)
- **Web search tool:** Tavily
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (384 numbers per text) and Ollama `nomic-embed-text` (768 numbers per text)
- **Vector stores:** FAISS and Chroma
- **Data loaders:** text files, PDF (`pypdf`), websites (`WebBaseLoader` with BeautifulSoup), Wikipedia, JSON from an API
- **Serving:** LangServe + FastAPI + uvicorn
- **Speech to text:** OpenAI Whisper (English) and Sarvam AI `saaras:v4` (Hindi)
- **Web frameworks:** Flask, FastAPI, Streamlit
- **Databases:** SQLite
- **Other:** yt-dlp, pydub, ffmpeg, mss (screenshots), pynput (hotkeys), Tkinter (desktop window), pypdf, BeautifulSoup
- **Package tools:** `uv` (`pyproject.toml`, `uv.lock`) and `pip` (`requirements.txt`)

---

## 4. Folder structure

```
genai/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── requirements.txt
├── uv.lock
│
├── src/
│   └── chatbot/
│       └── __init__.py
│
├── langchain_ex/
│   ├── 001_data_ingestion/
│   │   ├── data_ingestion.ipynb
│   │   └── speech.txt
│   ├── 002_data_transformer/
│   │   ├── text_spliting.ipynb
│   │   ├── character_text_splitter.ipynb
│   │   ├── html_text_splitter.ipynb
│   │   ├── json_splitting.ipynb
│   │   ├── speech.txt
│   │   └── ugc_ad_script.pdf
│   ├── 003_Embeddings/
│   │   ├── hugging_face_embedding.ipynb
│   │   └── ollama_embedding.ipynb
│   ├── 004_vectore_store/
│   │   ├── faiss.ipynb
│   │   ├── chroma_db.ipynb
│   │   ├── speech.txt
│   │   ├── faiss_index/ (index.faiss, index.pkl)
│   │   └── chroma_db/ (chroma.sqlite3 + <id>/ with 4 .bin files)
│   └── 005_LLM/
│       ├── llm.ipynb
│       ├── llm_creation.ipynb
│       ├── llm_with_history.ipynb
│       ├── chat_bot.ipynb
│       ├── RAG_APP.ipynb
│       ├── rag2.ipynb
│       ├── serve.py
│       ├── genai_app_with_ollama/main.py
│       └── __pycache__/serve.cpython-312.pyc
│
├── updated_langchain/
│   ├── agents.ipynb
│   ├── pydantic_structured_output.ipynb
│   ├── typedict_structured_output.ipynb
│   ├── dataclass_structured_op.ipynb
│   ├── streaming_and_batch.ipynb
│   ├── middleware.ipynb
│   └── human_in_the_loop_middleware.ipynb
│
├── basic_chatbot/
│   ├── basic_chatbot.ipynb
│   ├── chatbot_withmemory_langraph.ipynb
│   ├── chatbot_for_joke.ipynb
│   ├── chat_humanintheloop.ipynb
│   ├── email_humanintheloop.ipynb
│   ├── debugging.ipynb
│   ├── fault_tolerance.ipynb
│   ├── parallel_runnables.ipynb
│   ├── runnable_passthorugh.py
│   ├── screen_reader.ipynb
│   ├── simple_multiaiagent.ipynb
│   ├── superviser_multiai_agent.ipynb
│   └── sample.png
│
├── applymate-ai/
│   ├── main.py
│   ├── applymate_workflow.ipynb
│   ├── applymate_chatbot_new.ipynb
│   ├── templates/index.html
│   ├── static/app.js
│   └── static/style.css
│
├── rag/
│   ├── main.py
│   ├── backend.py
│   ├── index.html
│   ├── rag.ipynb
│   └── uploads/
│       └── 888890b03c0c4e239ce798217baf9edf.pdf
│
├── video_assistant/
│   ├── app.py
│   ├── main.py
│   ├── transcript.txt
│   ├── core/
│   │   ├── transcriber.py
│   │   ├── summarize.py
│   │   ├── extractor.py
│   │   ├── rag_engine.py
│   │   ├── vector_store.py
│   │   └── test.py
│   ├── utils/
│   │   └── audio_process.py
│   ├── chroma-db/<id>/ (data_level0.bin, header.bin, length.bin, link_lists.bin)
│   └── downloads/ (one .wav file and two .mp3 chunk files)
│
├── website-chatbot/
│   ├── main.py
│   └── templates/index.html
│
├── chat_with_db/
│   ├── sqlite.py
│   ├── agent.py
│   ├── sqlite_backend.py
│   └── sql_agent.ipynb
│
├── cineSage/
│   ├── main.py
│   └── cinesage.ipynb
│
├── qa_chatbot/
│   ├── backend.py
│   ├── frontend.py
│   └── frontend_resuming_chat.py
│
├── qa_chatbot_databse/
│   ├── backend.py
│   └── frontend.py
│
├── screen_reader/
│   └── screen_reader.py
│
├── mcp/
│   ├── math_server.py
│   ├── weather_server.py
│   └── client.py
│
├── human_in_the_loop_middleware/
│   ├── hitl_llm.ipynb
│   └── chatbot_to_purhase_stock.py
│
├── email_sending_agent/
│   └── email_sending.ipynb
│
├── movie_ticket_booking/
│   └── movie_booking.ipynb
│
└── restaurant-booking-systems/
    └── restaurant-booking-system.ipynb
```

---

## 5. Folder by folder explanation

### 5.1 Root files

| File | What it does |
|---|---|
| `README.md` | This file. |
| `.gitignore` | Tells Git to ignore Python cache, build folders, virtual environments (`.venv`), the secret `.env` file and database files (`*.db`, `*.sqlite3`, etc.). Because of this, the SQLite databases are **not** in the repo. You create them by running the scripts. |
| `.python-version` | Says the project uses Python **3.12**. |
| `pyproject.toml` | Project settings for `uv`. Project name is `chatbot`, needs Python 3.12 or newer, and lists the main libraries (LangChain, LangGraph, Chroma, FAISS, Flask, FastAPI, Streamlit, MCP and more). |
| `requirements.txt` | The same idea for `pip`, but a **longer list**. It also has the extra libraries needed by the video assistant and screen reader (Whisper, yt-dlp, pydub, mss, pynput, sarvamai, torch and others). |
| `uv.lock` | The exact versions of all libraries (about 213 packages) so that installs are repeatable with `uv`. |

### 5.2 `src/chatbot/`

- `__init__.py` - A tiny starter file with one function `main()` that prints "Hello from chatbot!". It is the default file that `uv init` creates. It is not used by the other projects.

---

### 5.3 `basic_chatbot/` - the LangGraph lessons

This folder is my notebook diary. Each file teaches one new idea. Almost all of them use Groq and load keys from `.env`.

| File | What it teaches |
|---|---|
| `basic_chatbot.ipynb` | **The very first chatbot.** Builds a `State` with `add_messages`, adds one node that calls the LLM, connects `START → node → END`, and runs it. Then adds tools (Tavily web search, a `multiply` function, a `weather` function) with a **conditional edge**. Shows a problem: when the graph ends right after the tool, the AI cannot use the tool answer. Fixes it by sending the tool result **back to the LLM** (`tools → llm` edge). |
| `chatbot_withmemory_langraph.ipynb` | **Memory.** Adds `MemorySaver` and a `thread_id`, so the bot remembers your name inside one thread but not in another thread. Also compares `stream_mode="updates"` (only the newest change) and `stream_mode="values"` (the full state). |
| `chatbot_for_joke.ipynb` | **Custom state and time travel.** State has `topic`, `joke` and `explaination`. Node 1 writes a joke, node 2 explains it. Then uses `get_state_history`, `get_state` and a checkpoint id to **go back to an earlier step and run again**. |
| `chat_humanintheloop.ipynb` | **Human-in-the-loop, basic.** A `human_assistance` tool calls `interrupt()` so the graph stops and waits. You continue it with `Command(resume="yes")`. |
| `email_humanintheloop.ipynb` | A `send_email` tool that asks "Do you want to send this email? yes/no" before going on. (It is a practice version - it does not really send mail.) |
| `debugging.ipynb` | **LangSmith tracing.** Turns on tracing with environment variables and runs a tiny graph with an `add` tool so you can inspect the steps in LangSmith. |
| `fault_tolerance.ipynb` | An **empty notebook** (one empty cell). A placeholder for a future lesson. |
| `parallel_runnables.ipynb` | **`RunnableParallel`.** Runs a "short explanation" chain and a "detailed explanation" chain at the same time. Then gives each chain a different topic using `RunnableLambda`. |
| `runnable_passthorugh.py` | A script using `RunnablePassthrough` and `RunnableParallel`. Chain 1 writes code for a question. Chain 2 takes that code and returns **both the code and a simple explanation**. |
| `screen_reader.ipynb` | **First test of the screen reader idea.** Takes a screenshot with `mss`, turns it into base64, and sends it to a vision model (`qwen/qwen3.8-27b`) to explain the screen. |
| `simple_multiaiagent.ipynb` | **Multi-agent, simple.** A *researcher* agent (uses Tavily search) hands over to a *writer* agent. Includes a loop so the researcher can call tools many times. At the end the graph explains its own code line by line. |
| `superviser_multiai_agent.ipynb` | **Multi-agent with a supervisor.** A supervisor checks what is missing and sends work to the *researcher*, then the *analysis* agent, then the *writer*, and stops when the report is done. Test run: a report on how AI is changing healthcare. |
| `sample.png` | A 1920x1080 screenshot (VS Code with this project open). It was saved by the screen-capture test and is just a sample image. |

---

### 5.4 `applymate-ai/` - ApplyMate AI (job application email agent)

**What it does:** You upload your resume (PDF), give your LinkedIn, GitHub, Gmail address and Gmail App Password. Then you chat: tell it the **company**, **job role** and **recruiter email**. It writes a personalised email from your resume, shows you a **draft**, and only sends it (with your resume attached) after you press **Send**. You can also type changes ("make it shorter") or cancel.

| File | What it does |
|---|---|
| `main.py` | The Flask server (runs on port **5000**). Pages and API routes: `/` (web page), `/api/status`, `/api/setup` (saves resume text and your details), `/api/chat` (talks to the agent), `/api/decision` (approve, reject or rewrite the draft). Inside there is a LangChain **agent** with two tools: `write_email` and `send_email`. A `HumanInTheLoopMiddleware` pauses the agent **only before `send_email`**. Emails go out through Gmail SMTP with the resume attached. The prompt strictly says: never invent the recruiter email, company or experience. |
| `templates/index.html` | The web page: setup form, chat window, draft card (with Send / Apply changes / Cancel buttons) and a guide on how to get a Gmail App Password. |
| `static/app.js` | The browser code. Shows the setup form, sends chat messages, shows the draft card, and sends your decision to the server. Makes a random `thread_id` for each browser visit. |
| `static/style.css` | The look of the page (blue theme, chat bubbles, cards). |
| `applymate_workflow.ipynb` | **Version 1** - built as a fixed LangGraph flow: `extract_info → draft_email → human_approval → send_email`. Sends an HTML + plain-text email with the resume attached. |
| `applymate_chatbot_new.ipynb` | **Version 2** - the chatty agent version (the base of `main.py`). Reads `SENDER_EMAIL` and `GMAIL_APP_PASSWORD` from `.env` and has a terminal loop for yes / no / edit. |

> The app saves the resume you upload into an `uploads/` folder and keeps sample resumes in `resumes/`. These folders are **no longer in the repo** (they held personal documents), so the app creates them when needed.

---

### 5.5 `rag/` - Nova AI (chat with your PDF)

**What it does:** Upload a PDF in the browser, then ask questions. Answers come from the PDF and include **page numbers**.

**How it works:** PDF → split into chunks (1000 characters, 100 overlap) → embeddings (`all-MiniLM-L6-v2`) → FAISS store → a `rag_tool` finds the best 5 chunks → a LangGraph chatbot uses the tool and answers.

| File | What it does |
|---|---|
| `backend.py` | `create_pdf_graph(pdf_path)` builds a complete RAG chatbot graph for one PDF. The system prompt says: always use the tool, do not invent facts, show page numbers. |
| `main.py` | FastAPI server. `GET /` shows the page. `POST /upload` accepts only PDF files up to **20 MB**, saves them in `uploads/` with a random name and returns a `session_id`. `POST /chat` takes `session_id` + `question` and returns the answer. Each session keeps its own graph in memory. |
| `index.html` | The "Nova AI" interface: drag-and-drop upload, suggestion buttons (summarize, key points, facts and dates, explain simply), chat bubbles with Markdown shown safely. |
| `rag.ipynb` | The first notebook version of the same idea, tested on a resume PDF. |
| `uploads/888890b0...pdf` | One PDF saved here by an earlier upload (a letter). The app saves every uploaded PDF in this folder with a random name. |

---

### 5.6 `video_assistant/` - Vidi AI (video intelligence)

**What it does:** Give a **YouTube link** or **upload a video / audio file**. It turns speech into text, then creates a **title, summary, action items, key decisions and open questions**. After that you can **chat with the video**, and answers come only from the transcript.

**The pipeline:**
`video/audio → WAV → small chunks → transcription → title + summary + extraction → vector store → question answering`

| File | What it does |
|---|---|
| `app.py` | The Streamlit website (dark purple theme). Sidebar: YouTube link, file upload, language (English or Hinglish). Tabs: Summary, Action Items, Key Decisions, Open Questions, Transcript (with a download button). Below that: a chat box to ask the video questions. |
| `main.py` | `run_pipeline(source, language)` joins all steps together and returns one result dictionary. Also works in the terminal: run it, enter a link, then chat. |
| `core/transcriber.py` | Speech to text. **English** uses OpenAI **Whisper** (`small` model). **Hindi** uses **Sarvam AI** (`saaras:v4`, `hi-IN`) with 3 retries. |
| `core/summarize.py` | Makes the summary in two rounds: summarise each 3000-character piece, then combine them into one bullet-point summary. Also `get_title()` makes a title of at most 8 words. |
| `core/extractor.py` | Finds **action items** (task, owner, deadline), **key decisions** and **open questions**. Works piece by piece, then merges the lists and removes duplicates. |
| `core/vector_store.py` | Cuts the transcript into 500-character chunks (200 overlap), makes embeddings and stores them in **Chroma** (collection `VIDEO-ASSISTANT`, saved in `./chroma-db`). |
| `core/rag_engine.py` | Builds the question-answer chain (finds the best 4 chunks, answers only from them, says "not found" if the answer is missing). Also has `load_rag_chain()` to reuse a saved database. |
| `core/test.py` | A quick test script. Transcribes a Hindi YouTube video, saves `transcript.txt` and prints the extracted items. |
| `utils/audio_process.py` | Downloads YouTube audio with `yt-dlp`, converts any file to mono 16 kHz WAV, and cuts audio into chunks (4 minutes normally, 25 seconds for Hindi because Sarvam allows about 30 seconds). |
| `transcript.txt` | A saved sample transcript (a mix of Hindi and English) of a different test video. |
| `chroma-db/` | The saved Chroma vector database files (`data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin`). Generated automatically - not meant to be read. |
| `downloads/` | Sample audio from a test run on the video "What Is LLM Inference? How AI Models Generate Responses": one large `.wav` file (about 89 MB) and two `.mp3` chunk files. |

> You need **ffmpeg** installed on your computer for audio conversion.

---

### 5.7 `website-chatbot/` - Scrap business assistant

**What it does:** A customer-support chatbot for **Shah Industries (Ratnagiri Scrap)**. It reads pages from the business website, and answers questions about scrap types, services and contact details. It never invents prices or contact info.

| File | What it does |
|---|---|
| `main.py` | FastAPI server. At start-up it **loads 5 pages** of the business website (home, about, services, FAQ, contact), cuts them into chunks (2000 / 500 overlap), and stores them in FAISS. It uses a **history-aware retriever** (first rewrites your question using the earlier chat) and then answers using only the website text. Route `POST /chat` takes `{"message": "..."}`. |
| `templates/index.html` | The chat page: company introduction, list of scrap materials, quick-question buttons and the chat window. |

---

### 5.8 `chat_with_db/` - Chat with a SQL database

**What it does:** Pick a table, ask a question in plain English ("How many students are in class 12?"), and the AI writes and runs the SQL for you (read-only).

| File | What it does |
|---|---|
| `sqlite.py` | Run this **first, once**. It creates `student.db` with a `students` table (`ID`, `name`, `class`) and inserts 8 sample students. |
| `agent.py` | Connects to the database. `get_table_agent(table_name)` builds a SQL agent that can see **only the selected table**. Its prompt says: do not invent results and never INSERT, UPDATE, DELETE, DROP, ALTER or CREATE. |
| `sqlite_backend.py` | The Streamlit app **"SQL AI Explorer"** (dark theme): choose a table in the sidebar, see cards (tables, rows, columns), chat in one tab, and preview the first 10 rows and column types in another tab. Has suggestion buttons and a "Clear chat" button. |
| `sql_agent.ipynb` | The notebook version used to test the SQL agent before building the app. |

---

### 5.9 `cineSage/` - Movie information extractor

**Story:** *CineSage Analytics* wants a tool that takes a messy movie paragraph, pulls out important facts, writes a summary, returns **JSON**, and stores it in a database.

| File | What it does |
|---|---|
| `main.py` | Streamlit app. Paste a paragraph → get movie name, director, release year, genres, lead actors, a summary and a **"missing information"** list. You can view / download the JSON and click **Add into DB** to save it into a SQLite `movies` table. |
| `cinesage.ipynb` | The notebook where it was built. Tries two ways to get structured data: `with_structured_output(MovieInfo)` (Pydantic) and `JsonOutputParser`, then saves one record into SQLite. |

---

### 5.10 `qa_chatbot/` - Simple chat app (memory in RAM)

| File | What it does |
|---|---|
| `backend.py` | `create_app(groq_api_key)` builds a one-node LangGraph chatbot with `MemorySaver`. It sends only the **last 6 messages** to the LLM to keep requests small. |
| `frontend.py` | Streamlit chat page with a dark indigo / pink design. You type your **Groq API key** and a **chat session ID** in the sidebar. |
| `frontend_resuming_chat.py` | A better version: key comes from `.env`, there is a **NEW CHAT** button, a **Conversation History** list in the sidebar to reopen old chats, and the answer is **streamed** word by word. |

> Memory is in RAM, so the history disappears when you stop the app.

---

### 5.11 `qa_chatbot_databse/` - Chat app with saved memory

Same idea as `qa_chatbot`, but chats are **saved in a SQLite file** (`chatbot_with_db.db`) using `SqliteSaver`, so they are still there after you restart.

| File | What it does |
|---|---|
| `backend.py` | Builds the same one-node chatbot with `SqliteSaver`, and reads the database to collect all old `thread_id`s into `list_of_threads`. |
| `frontend.py` | Streamlit app. You type a **chat name** (it becomes the thread ID), click **NEW CHAT**, and old chats appear in the sidebar. Streams the answers. |

---

### 5.12 `screen_reader/` - Screen Reader AI (Windows)

| File | What it does |
|---|---|
| `screen_reader.py` | A desktop helper made with **Tkinter**. A small floating **"AI"** button stays on your screen. Click it (or press **Ctrl + Alt + S**) and it hides itself, takes a screenshot, sends it to a vision model, and shows a clear answer: *What is happening, What is visible, Important details, Suggestions*. You can then ask **follow-up questions** about the same screenshot. Replies are forced to be in **English**. It removes hidden `<think>` text and shows simple Markdown (headings, bullets, code, tables). Built for **Windows**. |

---

### 5.13 `mcp/` - Model Context Protocol demo

| File | What it does |
|---|---|
| `math_server.py` | An MCP server with two tools, `add` and `multiply`. Talks over **stdio** (the client starts it automatically). |
| `weather_server.py` | An MCP server with one tool, `weather(location)`. It always answers "sunny" (a demo, not real weather). Runs over **streamable HTTP**. |
| `client.py` | Connects to **both** servers using `MultiServerMCPClient`, lists the tools, creates a ReAct agent and asks: "What is 2 + 2?" and "today's weather in ratnagiri". The weather server is expected at `http://localhost:8000/mcp`. |

---

### 5.14 `human_in_the_loop_middleware/`

| File | What it does |
|---|---|
| `hitl_llm.ipynb` | A graph where **every question must be approved** by a human (`y` / `n`) before the LLM answers. |
| `chatbot_to_purhase_stock.py` | A terminal **stock chatbot**. It gets live prices from the **Alpha Vantage** API, and when you ask to buy shares it **pauses and asks you yes / no**. The purchase is **only simulated** - no real trade happens. |

---

### 5.15 `email_sending_agent/`

- `email_sending.ipynb` - First sends a plain test email with Python `smtplib` through Gmail. Then builds an agent with a `send_email` tool that **asks for permission** (yes / no) before it sends. Tested for both "yes" and "no".

### 5.16 `movie_ticket_booking/`

- `movie_booking.ipynb` - A friendly ticket-booking agent. There are 3 slots (**10 AM, 12 PM, 2 PM**) with **20 seats** each. Tools: `check_slots`, `book_slot`, `show_bookings`. Booking needs your approval. Data is kept in memory only.

### 5.17 `restaurant-booking-systems/`

- `restaurant-booking-system.ipynb` - A table-reservation agent using **SQLite**. Two tables: `restaurant_tables` (`table-1` to `table-5`) and `restaurant_bookings`. Tools: `book_table` (safe database transaction, blocks double booking), `check_table_availability`, `view_bookings`. Final booking needs human approval.

---

### 5.18 `langchain_ex/` - LangChain basics course (5 parts)

This folder is a **step-by-step course**. The numbers `001` to `005` show the order. Each part builds on the one before it, and together they make a full RAG pipeline:

`load data → split into chunks → make embeddings → save in a vector store → ask an LLM`

#### `001_data_ingestion/` - Part 1: bring data in

| File | What it teaches |
|---|---|
| `data_ingestion.ipynb` | How to **load data from different places** into LangChain `Document` objects. Uses `TextLoader` (a `.txt` file), `PyPDFLoader` (a PDF on the computer and also a PDF from a web link - the "Attention Is All You Need" paper on arXiv), `WebBaseLoader` (a web page, and also only one part of a page using a BeautifulSoup `SoupStrainer` on the `post-title` class) and `WikipediaLoader` (2 pages about "Generative Ai"). Also shows that each result has `page_content` and `metadata`. |
| `speech.txt` | A short story, **"The Clockmaker of Ratnapur"** (old clockmaker Dinkar Rao and a grandfather clock he kept stopped for many years). It is the sample text used in the next lessons. The same file is copied into `002_data_transformer` and `004_vectore_store`. |

#### `002_data_transformer/` - Part 2: split the text

| File | What it teaches |
|---|---|
| `text_spliting.ipynb` | **`RecursiveCharacterTextSplitter`** - the most used splitter. Loads a PDF and splits it with `chunk_size=500, chunk_overlap=50`, then splits `speech.txt` with `chunk_size=100, chunk_overlap=20`. Explains `split_documents` (when you already have Documents) versus `create_documents` (when you have plain text strings). |
| `character_text_splitter.ipynb` | **`CharacterTextSplitter`** - splits only at **one separator you choose**. A small coffee text is split with `"\n\n"` and again with a space `" "`, so you can see how the separator changes the chunks (and how a chunk can become longer than `chunk_size`, which gives a warning). |
| `html_text_splitter.ipynb` | **`HTMLHeaderTextSplitter`** - splits web pages by headings (`h1`, `h2`, `h3`) and stores the heading names in the metadata. Tested on a small HTML string and on a Stanford Encyclopedia page (Gödel). |
| `json_splitting.ipynb` | **`RecursiveJsonSplitter`** - splits big JSON (here the LangSmith API `openapi.json`) into pieces of at most 500 characters. *(This notebook is about 2.4 MB because the whole JSON output is saved inside it.)* |
| `speech.txt` | Same short story as above. |
| `ugc_ad_script.pdf` | A 1-page sample PDF: a 30-second UGC ad script for a smart water bottle called **AquaLite**. Used to test PDF splitting. |

#### `003_Embeddings/` - Part 3: turn text into numbers

| File | What it teaches |
|---|---|
| `hugging_face_embedding.ipynb` | Uses `HuggingFaceEmbeddings` with `all-MiniLM-L6-v2`. `embed_query` turns one sentence into a list of **384 numbers**; `embed_documents` does the same for many sentences (3 sentences → 3 vectors of 384 numbers). Runs on your own computer. |
| `ollama_embedding.ipynb` | Uses `OllamaEmbeddings` with **`nomic-embed-text`**, which gives **768 numbers** per text. Needs Ollama running locally (`http://localhost:11434`). |

#### `004_vectore_store/` - Part 4: store and search the numbers

| File | What it teaches |
|---|---|
| `faiss.ipynb` | **FAISS** (Facebook AI Similarity Search). Loads `speech.txt` → splits (500 / 50) → Ollama embeddings → `FAISS.from_documents`. Then `similarity_search`, `similarity_search_with_score` (the score is an **L2 distance, so lower is better**), using the store `as_retriever()`, and **saving to disk** with `save_local('faiss_index')`. Has small text diagrams that explain the flow. |
| `chroma_db.ipynb` | **Chroma**, the same steps but with `Chroma.from_documents(..., persist_directory="./chroma_db")`. Shows `similarity_search`, `similarity_search_with_score` and `as_retriever`. |
| `speech.txt` | The same short story. |
| `faiss_index/` (`index.faiss`, `index.pkl`) | The **saved FAISS database** made by the notebook (the vectors and the text/metadata). Generated files, not meant to be read. |
| `chroma_db/` (`chroma.sqlite3` and one folder with `data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin`) | The **saved Chroma database** made by the notebook (16 stored chunks). Generated files, not meant to be read. |

#### `005_LLM/` - Part 5: bring in the LLM

| File | What it teaches |
|---|---|
| `llm.ipynb` | The first LLM steps with Groq (`openai/gpt-oss-120b`) and LangSmith tracing. `SystemMessage` + `HumanMessage` (an English → Urdu translator), `StrOutputParser`, joining steps with `\|` (**LCEL**), `ChatPromptTemplate` with `{language}` and `{input}`, and the chain `prompt \| llm \| parser`. Tested with Urdu and Konkani. |
| `llm_creation.ipynb` | A slower, beginner version: how to set API keys in the environment, install `groq`, create the `ChatGroq` model, call `llm.invoke`, look at the response object (`.content`), then add a prompt template and a parser. |
| `llm_with_history.ipynb` | **Memory for plain LLMs.** Shows that the model forgets your name, then fixes it: first by sending old messages by hand, then with `RunnableWithMessageHistory` + `ChatMessageHistory` and a `session_id` (new id = new chat). Adds `MessagesPlaceholder`, an extra `{language}` input (answers in Hindi) and **`trim_messages`** (keep only the last 70 tokens, start on a human message) together with `itemgetter` and `RunnablePassthrough.assign`. |
| `chat_bot.ipynb` | A **website Q&A bot**. Loads a company website (Yakron Tech), splits it, embeds it with HuggingFace, stores it in Chroma, and answers using the old-style chain `create_stuff_documents_chain` + `create_retrieval_chain` (from `langchain_classic`) with the top 5 chunks. Tested with "what does yakron technologies serve?" and "how do I contact them?". |
| `RAG_APP.ipynb` | A **full RAG walk-through** on a home-bakery menu website. Load → split (200 / 50) → HuggingFace embeddings → FAISS → prompt that says "use only the context" → `document_chain` → first tested with a hand-made document, then with a **retriever** and `create_retrieval_chain`. Explains why the retrieval chain is needed (the context must come from similarity search, not from you). Ends with a small `input()` question loop. |
| `rag2.ipynb` | A **tiny RAG on 6 pet sentences** (dogs, cats, goldfish, parrots, rabbits, hamsters). Splits them (50 / 25), embeds with Ollama `nomic-embed-text`, stores in Chroma, searches "cat" with scores, shows the `similarity_score_threshold` retriever idea (in comments), and answers "tell me about cats?" with Groq. |
| `serve.py` | **LangServe API.** Builds a translator chain (`prompt \| llm \| parser`) and publishes it with `add_routes(app, chain, path="/chain")` in a FastAPI app called "langchain server". You then get `POST /chain/invoke`, `/chain/batch` and `/chain/stream` (and docs at `/docs`). Runs with `uvicorn` on `localhost:8000`. |
| `genai_app_with_ollama/main.py` | A **Streamlit chatbot that runs fully on your computer**: "LangChain + Ollama AI Chatbot". Uses `ChatOllama` with `qwen2.5:0.5b`, a simple prompt and a parser. Type a question, get an answer. |
| `__pycache__/serve.cpython-312.pyc` | Python's automatic compiled copy of `serve.py`. It is not source code and should not be in the repo (see known issues). |

---

### 5.19 `updated_langchain/` - Newer LangChain features

Short notebooks on the **new LangChain 1.x style**. They use Groq (`openai/gpt-oss-120b` or `openai/gpt-oss-20b`) and `.env` for keys.

| File | What it teaches |
|---|---|
| `agents.ipynb` | **LLM versus agent.** An LLM has a knowledge cut-off date and cannot know today's weather. An agent = LLM + tools. Uses `create_agent` with a `get_weather(city)` function (the docstring matters because the AI reads it to decide when to use the tool) and asks "weather in ratnagiri". *(The first cell uses the model name `gpt-5`, which needs an OpenAI key. The Groq version in the next cell is the one that works with this repo's keys.)* |
| `pydantic_structured_output.ipynb` | **Structured output with Pydantic.** `llm.with_structured_output(...)` with a `get_details` class (name, age) → `get_details(name='Azra Patvi', age=22)`. Then a `movie` class, `include_raw=True` (also returns the raw AI message), and a **nested** class (`movie_details` with a list of `actor` objects, genres and an optional budget). Result is an **object** and the data is **validated**. |
| `typedict_structured_output.ipynb` | The same idea with **`TypedDict` + `Annotated`**. Result is a plain **dictionary** such as `{'name': 'Inception', 'rating': 8.8, 'year': 2010}`. The notebook notes: Pydantic gives an object and checks the data, TypedDict gives a dictionary and does not check. |
| `dataclass_structured_op.ipynb` | The same idea with a Python **`@dataclass`** (`name`, `years`, `ratings`). |
| `streaming_and_batch.ipynb` | **Streaming:** `llm.stream(...)` prints the answer piece by piece (like ChatGPT), with `flush=True` to show it at once. **Batch:** `llm.batch([...])` answers three questions (GenAI, RAG, LangChain) in one call. |
| `middleware.ipynb` | **`SummarizationMiddleware`.** Explains middleware as code that sits around the agent. The agent keeps memory with `InMemorySaver`; when the chat reaches **10 messages** it summarizes the old ones and keeps the **last 4**. Tested with a 12-question chat, ending with "What is my name and profession?". |
| `human_in_the_loop_middleware.ipynb` | **`HumanInTheLoopMiddleware`.** An agent with `read_email_tool` (no pause) and `send_email_tool` (pauses and allows **approve / edit / reject**). Three runs: **approve** (email sent), **reject** (agent refuses to send) and **edit** (the human changes the recipient, subject and body before it is sent). Each run uses its own `thread_id` and resumes with `Command(resume={"decisions": [...]})`. The tools only return text - no real email is sent. |

---

## 6. How to set up the project

### Step 1 - Get the code

```bash
git clone https://github.com/azrapatvi/genai.git
cd genai
```

### Step 2 - Create a virtual environment (Python 3.12)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate
```

### Step 3 - Install libraries

Use `requirements.txt` because it has **everything** (the video assistant and screen reader need extra libraries):

```bash
pip install -r requirements.txt
pip install uvicorn python-multipart
```

- `uvicorn` runs the FastAPI apps (`rag`, `website-chatbot`).
- `python-multipart` is needed for PDF upload in FastAPI.
- If you see an error about `langchain_classic` (website chatbot and the `langchain_ex/005_LLM` RAG notebooks), run `pip install langchain-classic`.
- For `langchain_ex/005_LLM/serve.py` you also need LangServe: `pip install "langserve[all]"`.
- For the Wikipedia loader in `001_data_ingestion` run `pip install wikipedia`.

Using `uv` instead:

```bash
uv sync
```

(`uv sync` installs only what is in `pyproject.toml`, so you may still need to add the extra libraries from `requirements.txt` for some folders.)

### Step 4 - Install ffmpeg (only for `video_assistant`)

Install **ffmpeg** from https://ffmpeg.org and make sure the command `ffmpeg` works in your terminal.

### Step 5 - Install Ollama (only for the local-model lessons)

Needed for `langchain_ex/003_Embeddings/ollama_embedding.ipynb`, `004_vectore_store`, `005_LLM/rag2.ipynb` and `005_LLM/genai_app_with_ollama`. Install Ollama from https://ollama.com, then download the two small models:

```bash
ollama pull qwen2.5:0.5b
ollama pull nomic-embed-text
```

Keep Ollama running in the background while you use these notebooks (it listens on `http://localhost:11434`).

### Step 6 - Create a `.env` file in the project root

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=any_project_name
LANGCHAIN_PROJECT2=any_project_name
OPENAI_API_KEY=your_openai_key
HF_TOKEN=your_huggingface_token
SARVAM_API_KEY=your_sarvam_key
SENDER_EMAIL=you@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password
```

Which keys do you need?

| Key | Needed for |
|---|---|
| `GROQ_API_KEY` | Almost everything |
| `TAVILY_API_KEY` | `basic_chatbot` notebooks with web search |
| `LANGCHAIN_API_KEY` | `debugging.ipynb`, `website-chatbot` (must be set there), and most `langchain_ex` / `updated_langchain` notebooks (they copy it into the environment) |
| `LANGCHAIN_PROJECT` | `langchain_ex/005_LLM/llm.ipynb` and `llm_creation.ipynb` (the LangSmith project name; any name works) |
| `LANGCHAIN_PROJECT2` | `langchain_ex/005_LLM/genai_app_with_ollama/main.py` (the app stops if it is missing) |
| `OPENAI_API_KEY` | Only read (not really used) in `llm_creation.ipynb` and `RAG_APP.ipynb`; `updated_langchain/agents.ipynb` first cell needs a real one because it asks for `gpt-5` |
| `HF_TOKEN` | `website-chatbot` (must be set there) |
| `SARVAM_API_KEY` | Hindi transcription in `video_assistant` |
| `SENDER_EMAIL`, `GMAIL_APP_PASSWORD` | Email notebooks (`applymate-ai` notebooks, `email_sending_agent`). The ApplyMate **web app** asks for these inside the browser instead. |

**How to get a Gmail App Password:** turn on 2-Step Verification in your Google account, then open https://myaccount.google.com/apppasswords, create a password, and copy the 16 characters. Never use your normal Gmail password.

> **Important:** `.env` is already listed in `.gitignore`. Never upload your keys to GitHub.

---

## 7. How to run each project

Run these commands **from inside the project's own folder** (many files use paths relative to their folder).

| Project | Commands | Then open |
|---|---|---|
| **ApplyMate AI** | `cd applymate-ai` then `python main.py` | http://localhost:5000 |
| **Nova AI (PDF chat)** | `cd rag` then `uvicorn main:app --reload` | http://localhost:8000 |
| **Website chatbot** | `cd website-chatbot` then `uvicorn main:app --reload` | http://localhost:8000 |
| **Vidi AI (video)** | `cd video_assistant` then `streamlit run app.py` | the link Streamlit prints |
| **Video assistant (terminal)** | `cd video_assistant` then `python main.py` | - |
| **Chat with database** | `cd chat_with_db` then `python sqlite.py` (once) then `streamlit run sqlite_backend.py` | the link Streamlit prints |
| **CineSage** | `cd cineSage` then `streamlit run main.py` | the link Streamlit prints |
| **Simple chat (RAM)** | `cd qa_chatbot` then `streamlit run frontend.py` | the link Streamlit prints |
| **Chat with history** | `cd qa_chatbot` then `streamlit run frontend_resuming_chat.py` | the link Streamlit prints |
| **Chat with saved memory** | `cd qa_chatbot_databse` then `streamlit run frontend.py` | the link Streamlit prints |
| **Screen reader (Windows)** | `cd screen_reader` then `python screen_reader.py` | click the floating **AI** button or press Ctrl + Alt + S |
| **MCP demo** | Terminal 1: `cd mcp` then `python weather_server.py`. Terminal 2: `cd mcp` then `python client.py` | - |
| **Stock chatbot** | `cd human_in_the_loop_middleware` then `python chatbot_to_purhase_stock.py` (type `exit` to stop) | - |
| **LangServe translator API** | `cd langchain_ex/005_LLM` then `python serve.py` | http://localhost:8000/docs (and `POST /chain/invoke`) |
| **Local Ollama chatbot** | Start Ollama and `ollama pull qwen2.5:0.5b`, then `cd langchain_ex/005_LLM/genai_app_with_ollama` and `streamlit run main.py` | the link Streamlit prints |
| **Code + explanation chain** | `cd basic_chatbot` then `python runnable_passthorugh.py` | - |
| **Notebooks** | Open any `.ipynb` in VS Code or Jupyter and run the cells from top to bottom | - |

> The `rag` and `website-chatbot` apps both use port 8000 by default. Run one at a time, or add `--port 8001` to the second one. The MCP weather server also uses port 8000.

---

## 8. Things to know before you run (known issues)

I read every file while writing this README. These are things I noticed. They are good "next steps" to improve the repo.

**Security and privacy**

- `human_in_the_loop_middleware/chatbot_to_purhase_stock.py` has an **Alpha Vantage API key written directly in the code**. Move it to `.env` and create a new key, because the old one is now public in Git history.
- The resume PDFs that were in `applymate-ai` and one PDF in `rag/uploads` have been removed - good. But `rag/uploads/888890b0...pdf` (a letter) is still there. Consider removing it and adding `uploads/` folders to `.gitignore`.
- `video_assistant/downloads` has an **89 MB** audio file. Large files make the repo slow. Consider ignoring `downloads/` and `chroma-db/`.
- `langchain_ex/005_LLM/llm_creation.ipynb` prints the **first 8 characters of the Groq API key** and the saved output is inside the notebook. Delete that cell output (and rotate the key if you are worried).
- Some notebook outputs in `langchain_ex` show local paths like `C:\Users\...` and web-page contents (including a business phone number from the Yakron website in `chat_bot.ipynb`). Clear the outputs before sharing if you do not want these public.
- `langchain_ex/004_vectore_store/chroma_db/` and `faiss_index/` are **generated data** and `langchain_ex/005_LLM/__pycache__/serve.cpython-312.pyc` is a compiled cache file. They are in the repo even though `.gitignore` lists `__pycache__/` and `*.sqlite3` (they were added before / forced). Remove them with `git rm --cached` and let Git ignore them.
- One FAISS file (`index.pkl`) is a Python **pickle**. Only load FAISS indexes that you made yourself (`allow_dangerous_deserialization=True` is needed because pickle files can run code).

**Paths and setup**

- Several files use **Windows paths that only work on the author's computer**, for example `E:\chatbot\...` in `chat_with_db/agent.py`, `chat_with_db/sqlite.py`, `chat_with_db/sqlite_backend.py` (through `agent.py`), `cineSage/main.py`, `video_assistant/utils/audio_process.py`, and in the notebooks. Change them to your own folder before running (or switch to relative paths).
- `requirements.txt` and `pyproject.toml` are **not the same list**. `requirements.txt` is the complete one.
- `fastapi` is installed, but `uvicorn` and `python-multipart` are not in the lists - install them yourself (see Step 3).
- `website-chatbot/main.py` needs `GROQ_API_KEY`, `HF_TOKEN` and `LANGCHAIN_API_KEY` **all** set, otherwise it stops at start-up.
- `website-chatbot` keeps **one shared chat history** for all visitors (it is a simple demo).
- `langserve` is **not** in `requirements.txt` or `pyproject.toml` (needed for `serve.py`), and neither are `langchain-classic` and `wikipedia`. Install them yourself (see Step 3).
- The `langchain_ex` notebooks need **Ollama running** and the two models pulled (Step 5). Without it, cells that use `OllamaEmbeddings` fail with a connection error.
- Many notebooks load files with plain names like `speech.txt` and `ugc_ad_script.pdf`, so **start Jupyter from inside that notebook's folder** (each part has its own copy of `speech.txt`). `data_ingestion.ipynb` also reads a personal file from `C:\Users\Azrap\Downloads\resume.pdf` - change it to any PDF you have.
- `langchain_ex/001_data_ingestion/data_ingestion.ipynb` has a cell that says arXiv is "not supported now" and uses `PyPDFLoader` with the arXiv PDF link instead - that is the working way. The `pip install --force-reinstall "arxiv<2"` cell is not needed for it.
- `langchain_ex` notebooks use older import paths from `langchain_community` (it prints a "being sunset" warning) and the old chains from `langchain_classic`. They still work, but newer code should use `langchain_huggingface`, `langchain_ollama` and `langchain_chroma`.

**Small bugs worth fixing**

- `human_in_the_loop_middleware/chatbot_to_purhase_stock.py`: if you answer **no**, the graph is not resumed, so it asks the same question again. It also creates a new bot every turn, so memory is lost between messages.
- `restaurant-booking-systems/restaurant-booking-system.ipynb`: `get_bookings()` reads a table called `bookings`, but the real table is `restaurant_bookings`, so `view_bookings` will fail. The prompt also mentions `get_valid_table_ids()`, which does not exist.
- `video_assistant/main.py`: `run_pipeline` calls `process_input(source)` **without the language**, so Hindi audio is cut into 4-minute pieces instead of the 25-second pieces that Sarvam needs. (`core/test.py` passes the language correctly.) Also the terminal asks for "english/hinglish", but the code checks for `"hi"`.
- `video_assistant/core/vector_store.py`: every video adds to the **same** Chroma collection, so old videos can mix with new ones.
- `chat_with_db/sqlite.py`: running it twice inserts the 8 students again (duplicates).
- `cineSage/main.py`: the `MovieInfo` Pydantic class is defined but not used by the chain (the app uses `JsonOutputParser`).
- `basic_chatbot/fault_tolerance.ipynb` is empty and `src/chatbot/__init__.py` is only the default starter.
- `langchain_ex/005_LLM/genai_app_with_ollama/main.py`: the line `os.environ['LANGCHAIN_PROJECT2']=os.getenv("LANGCHAIN_PROJECT2")` crashes if that variable is not in `.env`. Also `LANGCHAIN_TRACING_V3` is not a real LangChain setting (the real one is `LANGCHAIN_TRACING_V2`), so tracing is not switched on. The app does not need either line to work.
- `langchain_ex/005_LLM/serve.py` imports `streamlit` but never uses it, and only sets `LANGCHAIN_API_KEY` (it needs `GROQ_API_KEY` in `.env` too, which `ChatGroq` reads by itself).
- `langchain_ex/005_LLM/rag2.ipynb` calls `llm.invoke("hello")` before the RAG chain - harmless, but it needs `GROQ_API_KEY` to be loaded; the notebook does that in an earlier cell.
- `langchain_ex/005_LLM/llm_with_history.ipynb` has a cell `GROQ_API_KEY is None` (a quick check, not a fix) and the `RAG_APP.ipynb` last cell waits for `input()`.
- `updated_langchain/agents.ipynb`: the first `create_agent` cell uses `model='gpt-5'`, which fails without an OpenAI key. Skip it and run the Groq cell.

---

## 9. Suggested learning order

If you want to learn from this repo, follow this path:

1. `langchain_ex/001_data_ingestion` - Load text, PDF, web and Wikipedia data
2. `langchain_ex/002_data_transformer` - Split text into chunks
3. `langchain_ex/003_Embeddings` - Turn text into numbers
4. `langchain_ex/004_vectore_store` - FAISS and Chroma
5. `langchain_ex/005_LLM` - Prompts, parsers, chat history, RAG, LangServe API, Ollama app
6. `updated_langchain` - Agents, structured output, streaming, middleware
7. `basic_chatbot/basic_chatbot.ipynb` - LangGraph: State, nodes, edges, tools
8. `basic_chatbot/chatbot_withmemory_langraph.ipynb` - Memory and threads
9. `basic_chatbot/parallel_runnables.ipynb` and `runnable_passthorugh.py` - Chains and parallel work
10. `basic_chatbot/chat_humanintheloop.ipynb` and `email_humanintheloop.ipynb` - Pause and ask a human
11. `basic_chatbot/simple_multiaiagent.ipynb` then `superviser_multiai_agent.ipynb` - Many agents working together
12. `rag/rag.ipynb` then the `rag/` app - Chat with documents
13. `cineSage`, `chat_with_db` - Structured output and databases
14. `movie_ticket_booking`, `restaurant-booking-systems`, `email_sending_agent` - Real tasks with approval steps
15. `mcp` - Tools as servers
16. `applymate-ai`, `video_assistant`, `website-chatbot`, `screen_reader` - Full projects

---

## 10. Author

**Azra Patvi** - AI and Data Science student and developer.
GitHub: [@azrapatvi](https://github.com/azrapatvi)

If this repo helped you, give it a star.
