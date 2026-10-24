# Simple Q&A Chatbot

A basic chat app. It remembers the chat while the app is running, but forgets everything when you stop it.

## Files
| File | What it does |
|---|---|
| `backend.py` | The chatbot (LangGraph with memory in RAM) |
| `frontend.py` | Streamlit page. You type your Groq key in the sidebar |
| `frontend_resuming_chat.py` | Better page: key from `.env`, New Chat button, old chats list, word-by-word answers |

## Run it
```
streamlit run frontend_resuming_chat.py
```

## Notes
- Only the last 6 messages are sent to the AI to keep it fast.
