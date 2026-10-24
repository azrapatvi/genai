# ApplyMate AI

A web app that writes job application emails for you. It sends the email only after you say yes.

## How it works
1. Upload your resume (PDF) and add your LinkedIn, GitHub and Gmail details.
2. Tell the chat the **company**, **job role** and **recruiter email**.
3. The AI writes a draft email from your resume.
4. You choose: **Send**, **Apply changes** or **Cancel**.
5. If you press Send, the email goes out with your resume attached.

## Files
| File | What it does |
|---|---|
| `main.py` | The Flask server (port 5000) with the AI agent |
| `templates/index.html` | The web page |
| `static/app.js` | The browser code |
| `static/style.css` | The design |
| `applymate_workflow.ipynb` | Version 1 (fixed flow) |
| `applymate_chatbot_new.ipynb` | Version 2 (chat agent) |

## Run it
```
python main.py
```
Then open `http://localhost:5000`.

## Notes
- Add `GROQ_API_KEY` to a `.env` file.
- Use a Gmail **App Password**, not your normal password. Create one at https://myaccount.google.com/apppasswords
- The app never invents the recruiter email or company name. It asks you.
