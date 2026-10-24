from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

import mss
import base64
import re
import ctypes
import threading
import tkinter as tk
from tkinter import ttk
from io import BytesIO
from PIL import Image, ImageTk
from pynput import keyboard

# Sharper UI on Windows high-DPI screens
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

load_dotenv()

# Keep your original model
llm = ChatGroq(model="qwen/qwen3.8-27b")

# Forces English output (fixes the Korean replies)
SYSTEM_PROMPT = SystemMessage(content=(
    "You are Screen Reader AI. You MUST reply in English only, "
    "no matter what language appears on the screen or in the question. "
    "If the screen contains other languages, quote them as-is but explain "
    "everything in English. Use clear markdown: headings, bullets and "
    "code formatting where useful."
))

CAPTURE_PROMPT = (
    "Look at this screenshot of my screen and reply in English only, "
    "using exactly this structure:\n\n"
    "## What is happening\n"
    "2-3 sentences describing what the user seems to be doing right now.\n\n"
    "## What is visible\n"
    "- Bullet list of the apps, windows, tabs, menus and main UI elements.\n\n"
    "## Important details\n"
    "- Any readable text, code, numbers, errors or data shown on screen.\n\n"
    "## Suggestions\n"
    "- Helpful next steps or fixes if something looks wrong "
    "(skip this section if nothing needs attention)."
)

last_image_message = None
last_preview = None
image_refs = []          # keep PhotoImage objects alive
chat_history = []
busy = False

BG = "#0F172A"
PANEL = "#1E293B"
INPUT_BG = "#334155"
ACCENT = "#14B8A6"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
USER_BG = "#1D4ED8"
CODE_BG = "#0B1220"


# ---------------- HELPERS ----------------

def clean_answer(content):
    """Turn model output into clean text (handles list content and <think> blocks)."""
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))
        content = "\n".join(parts)

    text = str(content)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"</?think>", "", text)
    return text.strip()


# ---------------- SCREENSHOT ----------------

def capture_ss():
    global last_image_message, last_preview

    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])

        image = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

    # Compress screenshot to reduce request size
    image.thumbnail((768, 768))

    # Small copy to show inside the chat window
    preview = image.copy()
    preview.thumbnail((420, 280))
    last_preview = preview

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=50, optimize=True)

    encoded_image = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    image_url = f"data:image/jpeg;base64,{encoded_image}"

    message = HumanMessage(content=[
        {
            "type": "text",
            "text": CAPTURE_PROMPT
        },
        {
            "type": "image_url",
            "image_url": {"url": image_url}
        }
    ])

    last_image_message = message
    return message


# ---------------- MARKDOWN DISPLAY ----------------

def insert_inline(text, base_tag=None):
    parts = re.split(r"(\*\*.*?\*\*|`[^`]+`)", text)

    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            output.insert("end", part[2:-2], ("bold",))
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            output.insert("end", part[1:-1], ("inline_code",))
        else:
            output.insert("end", part, (base_tag,) if base_tag else ())


def insert_markdown(text):
    output.config(state="normal")
    in_code = False

    for line in str(text).splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            output.insert("end", "  " + line + "\n", "code")
        elif not stripped:
            output.insert("end", "\n", "gap")
        elif re.match(r"^[-*_]{3,}$", stripped):
            output.insert("end", "─" * 38 + "\n", "rule")
        elif stripped.startswith("#"):
            output.insert(
                "end",
                stripped.lstrip("#").strip().replace("**", "") + "\n",
                "heading"
            )
        elif stripped.startswith("|"):
            # simple table support
            if re.match(r"^\|[\s:\-|]+\|?$", stripped):
                continue
            cells = [c.strip().replace("**", "").replace("`", "")
                     for c in stripped.strip("|").split("|")]
            output.insert("end", "  " + "  │  ".join(cells) + "\n", "table")
        elif stripped.startswith(("- ", "* ", "+ ")):
            indent = len(line) - len(line.lstrip())
            tag = "bullet_line2" if indent >= 2 else "bullet_line"
            output.insert("end", "•  ", ("bullet", tag))
            insert_inline(stripped[2:], tag)
            output.insert("end", "\n", tag)
        elif re.match(r"^\d+[.)]\s+", stripped):
            match = re.match(r"^(\d+[.)])\s+(.*)$", stripped)
            output.insert("end", match.group(1) + "  ", ("bullet", "bullet_line"))
            insert_inline(match.group(2), "bullet_line")
            output.insert("end", "\n", "bullet_line")
        elif stripped.startswith(">"):
            insert_inline(stripped.lstrip("> ").strip(), "quote")
            output.insert("end", "\n", "quote")
        else:
            insert_inline(line)
            output.insert("end", "\n")

    output.insert("end", "\n")
    output.see("end")
    output.config(state="disabled")


def add_message(speaker, text):
    output.config(state="normal")

    if speaker == "You":
        output.insert("end", "  You  \n", "speaker_user")
    elif speaker == "Error":
        output.insert("end", "  Error  \n", "speaker_error")
    else:
        output.insert("end", "  Screen Reader AI  \n", "speaker_ai")

    output.config(state="disabled")
    insert_markdown(text)


def add_image(pil_image):
    """Show the captured screenshot inside the chat."""
    if pil_image is None:
        return

    photo = ImageTk.PhotoImage(pil_image)
    image_refs.append(photo)

    output.config(state="normal")
    output.insert("end", "\n")
    output.image_create("end", image=photo, padx=10, pady=4)
    output.insert("end", "\n\n")
    output.see("end")
    output.config(state="disabled")


# ---------------- WINDOW SETUP ----------------

root = tk.Tk()
root.withdraw()

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

# Floating button (placed at bottom-right of whatever screen you have)
bubble = tk.Toplevel(root)
bubble.geometry(f"62x62+{SCREEN_W - 100}+{SCREEN_H - 170}")
bubble.overrideredirect(True)
bubble.attributes("-topmost", True)
bubble.configure(bg=BG)

tk.Button(
    bubble,
    text="AI",
    font=("Segoe UI", 16, "bold"),
    bg=ACCENT,
    fg="#062B29",
    activebackground="#0D9488",
    activeforeground="#062B29",
    relief="flat",
    cursor="hand2",
    command=lambda: open_chat()
).pack(fill="both", expand=True)

# Chat window
CHAT_W = 520
CHAT_H = min(720, SCREEN_H - 120)

chat = tk.Toplevel(root)
chat.title("Screen Reader AI")
chat.geometry(f"{CHAT_W}x{CHAT_H}+{SCREEN_W - CHAT_W - 40}+40")
chat.minsize(420, 500)
chat.configure(bg=BG)
chat.attributes("-topmost", True)
chat.withdraw()

chat.columnconfigure(0, weight=1)
chat.rowconfigure(1, weight=1)

header = tk.Frame(chat, bg=PANEL, padx=14, pady=12)
header.grid(row=0, column=0, sticky="ew")
header.columnconfigure(0, weight=1)

tk.Label(
    header,
    text="Screen Reader AI",
    font=("Segoe UI", 15, "bold"),
    bg=PANEL,
    fg=TEXT
).grid(row=0, column=0, sticky="w")

capture_button = tk.Button(
    header,
    text="📷  Capture Screen",
    font=("Segoe UI", 10, "bold"),
    bg=ACCENT,
    fg="#062B29",
    activebackground="#0D9488",
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=4,
    command=lambda: start_capture()
)
capture_button.grid(row=0, column=1, padx=8)

# Output area
chat_area = tk.Frame(chat, bg=BG)
chat_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
chat_area.rowconfigure(0, weight=1)
chat_area.columnconfigure(0, weight=1)

output = tk.Text(
    chat_area,
    wrap="word",
    bg=BG,
    fg=TEXT,
    font=("Segoe UI", 11),
    relief="flat",
    padx=12,
    pady=10,
    spacing1=2,
    spacing3=2,
    borderwidth=0,
    highlightthickness=0,
    cursor="arrow",
    state="disabled"
)
output.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(
    chat_area,
    orient="vertical",
    command=output.yview
)
scrollbar.grid(row=0, column=1, sticky="ns")
output.configure(yscrollcommand=scrollbar.set)

output.tag_configure(
    "heading",
    font=("Segoe UI", 13, "bold"),
    foreground=ACCENT,
    spacing1=10,
    spacing3=4
)
output.tag_configure(
    "bold",
    font=("Segoe UI", 11, "bold"),
    foreground="#FFFFFF"
)
output.tag_configure(
    "code",
    font=("Consolas", 10),
    background=CODE_BG,
    foreground="#A7F3D0",
    lmargin1=10,
    lmargin2=10,
    spacing1=0,
    spacing3=0
)
output.tag_configure(
    "inline_code",
    font=("Consolas", 10),
    background=CODE_BG,
    foreground="#A7F3D0"
)
output.tag_configure(
    "bullet",
    foreground=ACCENT,
    font=("Segoe UI", 11, "bold")
)
output.tag_configure("bullet_line", lmargin1=12, lmargin2=30)
output.tag_configure("bullet_line2", lmargin1=34, lmargin2=52)
output.tag_configure(
    "quote",
    foreground=MUTED,
    lmargin1=14,
    lmargin2=14,
    font=("Segoe UI", 11, "italic")
)
output.tag_configure(
    "table",
    font=("Consolas", 10),
    foreground=TEXT,
    background=PANEL
)
output.tag_configure("rule", foreground=MUTED)
output.tag_configure("gap", font=("Segoe UI", 4))
output.tag_configure(
    "speaker_ai",
    foreground="#062B29",
    background=ACCENT,
    font=("Segoe UI", 9, "bold"),
    spacing1=10,
    spacing3=4
)
output.tag_configure(
    "speaker_user",
    foreground="#FFFFFF",
    background=USER_BG,
    font=("Segoe UI", 9, "bold"),
    spacing1=10,
    spacing3=4
)
output.tag_configure(
    "speaker_error",
    foreground="#FFFFFF",
    background="#DC2626",
    font=("Segoe UI", 9, "bold"),
    spacing1=10,
    spacing3=4
)

# Question input
bottom = tk.Frame(chat, bg=PANEL, padx=12, pady=10)
bottom.grid(row=2, column=0, sticky="ew")
bottom.columnconfigure(0, weight=1)

question_entry = tk.Entry(
    bottom,
    font=("Segoe UI", 11),
    bg=INPUT_BG,
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat"
)
question_entry.grid(
    row=0, column=0, sticky="ew", ipady=8, padx=(0, 8)
)

send_button = tk.Button(
    bottom,
    text="Send",
    font=("Segoe UI", 10, "bold"),
    bg=ACCENT,
    fg="#062B29",
    activebackground="#0D9488",
    relief="flat",
    cursor="hand2",
    padx=14,
    pady=5,
    command=lambda: send_question()
)
send_button.grid(row=0, column=1)

status_label = tk.Label(
    bottom,
    text="Ready",
    font=("Segoe UI", 9),
    bg=PANEL,
    fg=MUTED
)
status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))


# ---------------- CHAT ACTIONS ----------------

def open_chat():
    chat.deiconify()
    chat.lift()
    chat.attributes("-topmost", True)
    question_entry.focus_set()


def set_busy(value, message):
    global busy
    busy = value

    status_label.config(text=message)

    state = "disabled" if value else "normal"
    capture_button.config(state=state)
    send_button.config(state=state)
    question_entry.config(state=state)

    if not value:
        question_entry.focus_set()


# Hide the UI only while taking the screenshot
def start_capture():
    if busy:
        return

    set_busy(True, "Capturing screen...")

    chat.withdraw()
    bubble.withdraw()

    # Give Windows time to repaint before screenshot capture
    root.after(400, do_capture)


def do_capture():
    try:
        # Only capture the screenshot here.
        # Do not wait for the AI response here.
        message = capture_ss()

    except Exception as error:
        bubble.deiconify()
        open_chat()
        add_message("Error", str(error))
        set_busy(False, "Ready")
        return

    # Restore windows immediately after the screenshot is captured
    bubble.deiconify()
    open_chat()

    # Show the screenshot in the chat, then the explanation below it
    add_message("You", "Captured my screen:")
    add_image(last_preview)

    set_busy(True, "Screenshot captured. AI is analyzing...")

    def worker():
        global chat_history

        try:
            # Your original LangChain call (+ English-only system prompt)
            response = llm.invoke([SYSTEM_PROMPT, message])
            answer = clean_answer(response.content)

            # Keep history text-only to avoid resending a large image
            chat_history = [
                HumanMessage(content="Explain the captured screen."),
                AIMessage(content=answer)
            ]

            root.after(
                0,
                lambda a=answer: capture_complete(a, None)
            )

        except Exception as error:
            root.after(
                0,
                lambda e=str(error): capture_complete(None, e)
            )

    threading.Thread(target=worker, daemon=True).start()


def capture_complete(answer, error):
    bubble.deiconify()
    chat.deiconify()
    chat.lift()

    if error:
        add_message("Error", error)
    else:
        add_message("AI", answer)

    set_busy(False, "Ready")


def send_question():
    if busy:
        return

    question = question_entry.get().strip()

    if not question:
        return

    question_entry.delete(0, "end")
    add_message("You", question)
    set_busy(True, "Thinking...")

    def worker():
        global chat_history

        try:
            # Preserve your screenshot-follow-up behavior
            if last_image_message is not None:
                message = HumanMessage(content=[
                    {"type": "text", "text": question + "\n\n(Reply in English only.)"},
                    last_image_message.content[1]
                ])
            else:
                message = HumanMessage(content=question + "\n\n(Reply in English only.)")

            response = llm.invoke([SYSTEM_PROMPT] + chat_history + [message])
            answer = clean_answer(response.content)

            chat_history.extend([
                HumanMessage(content=question),
                AIMessage(content=answer)
            ])

            root.after(
                0,
                lambda a=answer: question_complete(a, None)
            )

        except Exception as error:
            root.after(
                0,
                lambda e=str(error): question_complete(None, e)
            )

    threading.Thread(target=worker, daemon=True).start()


def question_complete(answer, error):
    if error:
        add_message("Error", error)
    else:
        add_message("AI", answer)

    set_busy(False, "Ready")


# Keep the global shortcut from your original code
def on_screenshot():
    root.after(0, start_capture)


question_entry.bind("<Return>", lambda event: send_question())
chat.protocol("WM_DELETE_WINDOW", chat.withdraw)

add_message(
    "AI",
    "Hi! Click **Capture Screen** to read your screen, "
    "or type a question below."
)

print("Screen Reader AI is running!")
print("Click the floating AI button to open the chat.")
print("Press Ctrl + Alt + S to read your screen.")
print("Press Ctrl + C in this terminal to exit.")

hotkey_listener = keyboard.GlobalHotKeys({
    "<ctrl>+<alt>+s": on_screenshot
})
hotkey_listener.start()

root.mainloop()

hotkey_listener.stop()