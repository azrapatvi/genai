# 🏥 Hospital Appointment Booking Chatbot

A simple AI chatbot for **Sunrise Multi-Speciality Hospital**. Patients can talk to it in normal English to **check doctor timings, book an appointment, find their appointments, and update an appointment**.

It is built with **Python, LangChain, Groq (LLM), SQLite and FastAPI**, and has a nice chat web page.

---

## ✨ What can the bot do?

| Feature | What happens |
|---|---|
| Check availability | Tells the doctor's timing for morning or evening |
| Book appointment | Collects details, asks for confirmation, then saves it |
| Find appointments | Searches by the patient's phone number |
| Update appointment | Changes doctor, date, session, name or phone |

The bot is polite, asks **one question at a time**, and **never books anything until the patient says "yes, confirmed"**.

---

## 📁 Project Structure

```
booking/
│
├── sqlit_connection.ipynb     # Notebook: first practice with SQLite (create tables, test functions)
├── booking_bot.ipynb          # Notebook: builds and tests the full agent step by step
│
└── booking_bot/               # The real project (final code)
    ├── agent.py               # Creates the AI agent (LLM + tools + rules/system prompt)
    ├── tools.py               # 4 tools the agent can use (check, book, find, update)
    ├── database.py            # Creates the SQLite tables and adds the doctors
    ├── utils.py               # Helper: finds a doctor even if the name is typed differently
    ├── config.py              # Reads GROQ_API_KEY from the .env file
    ├── api.py                 # FastAPI server (connects the web page to the agent)
    ├── main.py                # Run the bot in the terminal (no website needed)
    ├── index.html             # The chat website (UI)
    ├── hospital.db            # SQLite database file
    └── .env                   # Your secret key (you create this, see below)
```

---

## 🧠 How does it work? (Simple flow)

```
Patient types message
        │
        ▼
 index.html (chat page)
        │   sends message + thread_id
        ▼
 api.py  (FastAPI  →  /chat)
        │
        ▼
 agent.py  (Groq LLM  +  rules)
        │   decides which tool to call
        ▼
 tools.py  ──►  hospital.db (SQLite)
        │
        ▼
 Reply goes back to the chat page
```

1. The patient writes a message on the website.
2. `api.py` sends it to the **agent**.
3. The agent (the LLM) reads the message and follows the rules in its **system prompt**.
4. When needed, it calls a **tool** (for example `book_appointment`) which reads or writes the **database**.
5. The final answer is shown in the chat.

Each chat has its own **thread_id**, so the bot remembers the conversation inside that chat.

---

## 🗄️ Database (SQLite)

File: `hospital.db`. It has **2 tables**.

**1. `doctors`**

| Column | Meaning |
|---|---|
| doctor_id | Unique number |
| name | Doctor name (`dr_sharma`, `dr_khan`) |
| morning_start / morning_end | Morning timing |
| break_start / break_end | Lunch break |
| evening_start / evening_end | Evening timing |

Default doctors:

| Doctor | Morning | Break | Evening |
|---|---|---|---|
| dr_sharma | 11:00 – 13:00 | 13:00 – 14:00 | 14:00 – 20:00 |
| dr_khan | 10:00 – 13:00 | 13:00 – 14:00 | 14:00 – 19:00 |

**2. `appointments`**

| Column | Meaning |
|---|---|
| appointment_id | Unique number |
| patient_name | Patient's name |
| phone | Patient's phone number |
| doctor_name | Doctor's name |
| appointment_date | Date of visit |
| session | `morning` or `evening` |
| queue_number | Token number for that doctor, date and session |

> ℹ️ **Queue number:** the first patient gets 1, the next gets 2, and so on (separately for each doctor, date and session). The exact consultation time is **not guaranteed**.

---

## 🛠️ The 4 Tools (in `tools.py`)

| Tool | What it does |
|---|---|
| `check_availability(dr_name, session)` | Returns the doctor's timing for morning/evening |
| `book_appointment(patient_name, phone, dr_name, appointment_date, session)` | Saves a new appointment and gives a queue number |
| `find_appointments(phone)` | Lists all appointments for a phone number |
| `update_appointment(appointment_id, ...)` | Updates an appointment and gives a new queue number |

**Smart doctor search (`utils.py`):** the user can type `Dr. Khan`, `dr khan`, `Dr.khan` or `dr_khan` — all work, because spaces and symbols are removed before matching.

---

## 📜 Rules the Bot Follows (System Prompt)

- Greet politely and collect: **name, doctor, date, session, phone**.
- Ask for missing information **one question at a time**.
- **Never guess or invent** doctor names, IDs, dates or queue numbers.
- **Always summarize and ask for confirmation** before booking or updating.
- Never say "booked" unless the tool really succeeded.
- No medical diagnosis or medical advice.
- Do not show other patients' private information.

---

## 🚀 How to Run

### 1. Requirements
- Python 3.10 or higher
- A free **Groq API key** → https://console.groq.com

### 2. Install packages

```bash
pip install langchain langchain-groq langchain-core langgraph fastapi uvicorn python-dotenv python-multipart
```

### 3. Create a `.env` file
Inside the `booking_bot` folder, make a file named `.env`:

```
GROQ_API_KEY=your_groq_api_key_here
```

> 🔒 Never upload your `.env` file to GitHub. Add `.env` to `.gitignore`.

### 4. Fix the database path (important!)
In `database.py`, the path is written for the author's Windows computer:

```python
DB_NAME = r"E:\chatbot\booking\booking_bot\hospital.db"
```

Change it to a path that works on your computer. The easy way:

```python
from pathlib import Path
DB_NAME = str(Path(__file__).parent / "hospital.db")
```

### 5a. Run on the website

```bash
cd booking_bot
uvicorn api:app --reload
```

Open **http://127.0.0.1:8000** in your browser and start chatting.

### 5b. Or run in the terminal

```bash
cd booking_bot
python main.py
```

Type `exit` to stop.

---

## 🌐 API Endpoints (`api.py`)

| Method | URL | Use |
|---|---|---|
| GET | `/` | Opens the chat page (`index.html`) |
| POST | `/new-chat` | Makes a new `thread_id` for a new conversation |
| POST | `/chat` | Sends `message` and `thread_id`, returns `{"reply": "..."}` |

---

## 🎨 Website (`index.html`)

- Clean teal hospital theme, works on **mobile and desktop**
- Sidebar with quick buttons: Book Appointment, Find a Doctor, My Appointments, Update Appointment
- "Typing..." indicator while the bot is thinking
- Bot replies are shown with nice formatting (lists, tables) and are **sanitized** (DOMPurify) for safety
- **New Chat** button starts a fresh conversation

---

## 📓 About the Notebooks

| Notebook | Purpose |
|---|---|
| `sqlit_connection.ipynb` | Practice: connect to SQLite, create tables, add doctors, try simple `check_availability` and `book_appointment` functions |
| `booking_bot.ipynb` | Turns those functions into LangChain tools, builds the agent, and tests a full chat |

The notebooks are for learning and testing. The final working code is inside the `booking_bot/` folder.

---

## ⚠️ Known Limits & Future Improvements

- **Chat memory is in RAM** (`InMemorySaver`). If the server restarts, old chats are forgotten. Use a database-backed saver for production.
- **thread_id counter resets** when the server restarts (it starts from 1 again), so old and new chats can get mixed. Using a random ID (like `uuid4`) is safer.
- **No double-booking check** and no limit on how many patients per session.
- **No date check** — past dates or wrong date formats are not blocked.
- **Doctor timing is not checked at booking time**, only when asked.
- **Phone number alone is not real identity proof.** Add OTP verification for real use.
- No cancel-appointment tool yet.
- No `requirements.txt` yet — add one so setup is one command.

---

## 🧰 Tech Stack

- **Python**
- **LangChain + LangGraph** – agent and memory
- **Groq** (`openai/gpt-oss-120b`) – the LLM
- **SQLite** – database
- **FastAPI** – backend
- **HTML, CSS, JavaScript** – chat UI

---

## 👩‍💻 Author

**Azra Patvi** — [GitHub: azrapatvi](https://github.com/azrapatvi)
