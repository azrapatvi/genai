# Q&A Chatbot With Saved Chats

Like `qa_chatbot`, but chats are saved in a SQLite file. Your old chats are still there after you restart.

## Files
| File | What it does |
|---|---|
| `backend.py` | The chatbot with `SqliteSaver` and a list of old chats |
| `frontend.py` | Streamlit page with New Chat button and chat history |

## Run it
```
streamlit run frontend.py
```

## Notes
- Add `GROQ_API_KEY` to a `.env` file.
- The database file is made when you run the app.
