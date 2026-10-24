# CineSage - Movie Info Extractor

Paste a messy paragraph about a movie. The app picks out the facts and gives you clean JSON.

## What you get
Movie name, director, release year, genres, lead actors, a short summary and a list of missing information. You can download the JSON or save it to a SQLite database.

## Files
| File | What it does |
|---|---|
| `main.py` | The Streamlit app |
| `cinesage.ipynb` | The notebook where it was built |

## Run it
```
streamlit run main.py
```

## Notes
- Add `GROQ_API_KEY` to a `.env` file.
