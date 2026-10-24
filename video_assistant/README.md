# Vidi AI - Video Assistant

Give it a YouTube link or a video/audio file. It writes the text, makes a summary and lets you chat with the video.

## What you get
- Title and summary
- Action items, key decisions and open questions
- Full transcript (you can download it)
- A chat box to ask questions about the video

## How it works
video → audio → small pieces → speech to text → summary → vector store → questions and answers

## Files
| File | What it does |
|---|---|
| `app.py` | The Streamlit website |
| `main.py` | Runs the whole pipeline (also works in the terminal) |
| `core/transcriber.py` | Speech to text (Whisper for English, Sarvam AI for Hindi) |
| `core/summarize.py` | Title and summary |
| `core/extractor.py` | Action items, decisions, questions |
| `core/vector_store.py` | Saves the transcript in Chroma |
| `core/rag_engine.py` | Answers questions from the transcript |
| `core/test.py` | A quick test script |
| `utils/audio_process.py` | Downloads and cuts audio |
| `transcript.txt`, `downloads/`, `chroma-db/` | Sample and generated files |

## Run it
```
streamlit run app.py
```

## Notes
- Install **ffmpeg** on your computer first.
- Add `GROQ_API_KEY` to `.env`. For Hindi, also add `SARVAM_API_KEY`.
