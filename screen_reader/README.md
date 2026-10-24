# Screen Reader AI (Windows)

A small floating **AI** button that stays on your screen. Click it and the AI explains what you are looking at.

## How it works
1. Click the button (or press **Ctrl + Alt + S**).
2. The app takes a screenshot.
3. A vision AI model explains it: what is happening, what is visible, important details and suggestions.
4. You can ask follow-up questions about the same screenshot.

## File
| File | What it does |
|---|---|
| `screen_reader.py` | The whole desktop app (Tkinter) |

## Run it
```
python screen_reader.py
```

## Notes
- Made for Windows.
- Add `GROQ_API_KEY` to a `.env` file. It needs a model that can see images.
