# Chat With a Database

Ask questions in plain English and the AI writes the SQL for you. It can only read data (no changes).

Example: "How many students are in class 12?"

## Files
| File | What it does |
|---|---|
| `sqlite.py` | Run this first. Makes `student.db` with 8 sample students |
| `agent.py` | Builds the SQL agent for the table you pick |
| `sqlite_backend.py` | The Streamlit app "SQL AI Explorer" |
| `sql_agent.ipynb` | The notebook used to test the idea |

## Run it
```
python sqlite.py
streamlit run sqlite_backend.py
```

## Notes
- The database path in `sqlite.py` and `agent.py` is set to a Windows folder. Change it to your own path.
- Add `GROQ_API_KEY` to a `.env` file.
