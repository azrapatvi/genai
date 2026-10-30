from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from pathlib import Path
from agent import agent

app = FastAPI()

BASE_DIR = Path(__file__).parent

# Thread ID counter
thread_counter = 0


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/new-chat")
def new_chat():
    global thread_counter
    thread_counter += 1

    return {"thread_id": str(thread_counter)}


@app.post("/chat")
def chat(
    message: str = Form(...),
    thread_id: str = Form(...)
):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return {
        "reply": response["messages"][-1].content
    }