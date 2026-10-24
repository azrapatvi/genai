import streamlit as st
from backend import create_app, list_of_threads
from langchain.messages import HumanMessage
from langchain_core.messages import AIMessageChunk
import os
from dotenv import load_dotenv
import uuid

# ---------- UI ONLY: page config (must be the first Streamlit call) ----------
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- UI ONLY: styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp, button, input, textarea {
        font-family: 'Inter', sans-serif !important;
    }

    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* ---------- Background with soft glow ---------- */
    .stApp {
        background:
            radial-gradient(900px 500px at 85% -10%, rgba(99,102,241,0.22), transparent 60%),
            radial-gradient(700px 450px at 0% 10%, rgba(34,211,238,0.12), transparent 60%),
            #0a0d18;
        color: #e8ebf7;
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 7rem;
        max-width: 800px;
    }

    /* ---------- Main title ---------- */
    .stApp h1 {
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.8px;
        background: linear-gradient(90deg, #22d3ee 0%, #818cf8 55%, #c084fc 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.2rem;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: rgba(13,18,36,0.95);
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        letter-spacing: 1.5px;
    }
    section[data-testid="stSidebar"] label p {
        color: #9aa3c7 !important;
        font-size: 0.8rem !important;
    }

    /* Sidebar text input */
    section[data-testid="stSidebar"] input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #e8ebf7 !important;
        padding: 0.6rem 0.8rem !important;
    }
    section[data-testid="stSidebar"] input:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(129,140,248,0.25) !important;
    }

    /* Sidebar buttons (conversation list) */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        color: #d6dbf2;
        padding: 0.6rem 0.9rem;
        font-weight: 500;
        transition: all 0.18s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(129,140,248,0.14);
        border-color: rgba(129,140,248,0.55);
        color: #ffffff;
        transform: translateY(-1px);
    }

    /* NEW CHAT button: gradient */
    section[data-testid="stSidebar"] .stButton:first-of-type > button {
        background: linear-gradient(90deg, #22d3ee, #6366f1);
        border: none;
        color: #ffffff;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 6px 18px rgba(99,102,241,0.35);
    }
    section[data-testid="stSidebar"] .stButton:first-of-type > button:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
        color: #ffffff;
    }

    /* ---------- Chat messages ---------- */
    div[data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    /* User message: accent tint */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(34,211,238,0.10));
        border: 1px solid rgba(129,140,248,0.35);
    }

    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li {
        color: #e8ebf7;
        line-height: 1.65;
    }

    div[data-testid="stChatMessage"] pre {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* ---------- Chat input ---------- */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {
        background: transparent !important;
    }
    div[data-testid="stChatInput"] {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #818cf8;
        box-shadow: 0 0 0 3px rgba(129,140,248,0.25), 0 10px 30px rgba(0,0,0,0.35);
    }
    div[data-testid="stChatInput"] textarea {
        color: #e8ebf7 !important;
    }

    /* ---------- Chat name pill ---------- */
    .chat-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 999px;
        background: rgba(34,211,238,0.10);
        border: 1px solid rgba(34,211,238,0.35);
        color: #8ceaf9;
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }
    .chat-pill .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #22d3ee;
        box-shadow: 0 0 8px #22d3ee;
    }

    /* ---------- Welcome screen ---------- */
    .hero {
        text-align: center;
        padding: 3.2rem 1.5rem;
        margin-top: 1rem;
        border-radius: 24px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        box-shadow: 0 20px 50px rgba(0,0,0,0.35);
    }
    .hero .orb {
        width: 72px; height: 72px; margin: 0 auto 1.1rem auto;
        border-radius: 50%;
        background: conic-gradient(from 180deg, #22d3ee, #6366f1, #c084fc, #22d3ee);
        box-shadow: 0 0 40px rgba(99,102,241,0.55);
        display: flex; align-items: center; justify-content: center;
        font-size: 2rem;
    }
    .hero h2 {
        margin: 0 0 0.4rem 0;
        font-weight: 700;
        color: #ffffff;
        font-size: 1.5rem;
    }
    .hero p {
        margin: 0 auto;
        color: #9aa3c7;
        max-width: 440px;
        line-height: 1.6;
    }
    .hero .steps {
        display: flex; gap: 10px; justify-content: center;
        flex-wrap: wrap; margin-top: 1.4rem;
    }
    .hero .step {
        padding: 6px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        color: #c9d0ee;
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")


# Generate unique thread ID
def generate_threadi():
    return str(uuid.uuid4())


# Add thread ID to set
def add_thread_id(thread_id):
    if thread_id and thread_id.strip():
        st.session_state.list_of_thread_id.add(thread_id)


# Load previous conversation
def load_conversation(thread_id):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = app.get_state(config)

    messages = []

    for msg in state.values.get("messages", []):

        if msg.type == "human":
            messages.append({
                "role": "user",
                "content": msg.content
            })

        elif msg.type == "ai" and msg.content:
            messages.append({
                "role": "assistant",
                "content": msg.content
            })

    return messages


# Initialize LangGraph app only once
if "app" not in st.session_state:
    st.session_state.app = create_app(groq_api_key)

app = st.session_state.app


# Initialize session states
if "list_of_thread_id" not in st.session_state:
    st.session_state.list_of_thread_id = set(list_of_threads)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "message_history" not in st.session_state:
    st.session_state.message_history = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False


# SIDEBAR
st.sidebar.title("✨ CHATBOT")

# Enter chat name
chat_name = st.sidebar.text_input(
    "Enter chat name",
    key="new_chat_name",
    placeholder="e.g. Study help"
)

# New Chat Button
if st.sidebar.button("＋  NEW CHAT", use_container_width=True):

    if chat_name.strip():

        # Use chat name as thread ID (your original logic)
        st.session_state.thread_id = chat_name.strip()

        # Add thread ID to set
        add_thread_id(st.session_state.thread_id)

        # Clear old messages
        st.session_state.message_history = []

        # Enable chatbot
        st.session_state.chat_started = True

        st.rerun()

    else:
        st.sidebar.warning("Please enter a chat name.")


# Conversation History
st.sidebar.markdown("### Conversation History")

for thread_id in sorted(st.session_state.list_of_thread_id):

    # Skip invalid IDs
    if not isinstance(thread_id, str) or not thread_id.strip():
        continue

    # Mark the active conversation (UI only)
    label = ("🟣  " if thread_id == st.session_state.thread_id else "💬  ") + thread_id

    if st.sidebar.button(
        label,
        key=f"chat_{thread_id}",
        use_container_width=True
    ):

        # Select existing conversation
        st.session_state.thread_id = thread_id

        # Load saved messages
        st.session_state.message_history = load_conversation(
            thread_id
        )

        # Enable chatbot
        st.session_state.chat_started = True

        st.rerun()


# MAIN CHAT INTERFACE
st.title("AI Chatbot")


# Chat is available only after creating or selecting a conversation
if not st.session_state.chat_started:

    st.markdown(
        """
        <div class="hero">
            <div class="orb">✨</div>
            <h2>What's on your mind today?</h2>
            <p>Start a fresh conversation or jump back into an old one.
            Everything is saved in your history.</p>
            <div class="steps">
                <span class="step">1 · Enter a chat name</span>
                <span class="step">2 · Click NEW CHAT</span>
                <span class="step">3 · Start chatting</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        f'<span class="chat-pill"><span class="dot"></span>{st.session_state.thread_id}</span>',
        unsafe_allow_html=True,
    )

    # Display conversation messages
    for message in st.session_state.message_history:

        with st.chat_message(
            message["role"],
            avatar="🧑" if message["role"] == "user" else "🤖"
        ):
            st.write(message["content"])

    # User input
    user_input = st.chat_input("Ask me anything...")

    if user_input:

        # Current conversation configuration
        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id
            }
        }

        # Display user message
        with st.chat_message("user", avatar="🧑"):
            st.write(user_input)

        # Save user message in Streamlit history
        st.session_state.message_history.append({
            "role": "user",
            "content": user_input
        })

        # STREAMING RESPONSE
        with st.chat_message("assistant", avatar="🤖"):

            def stream_response():

                for chunk, metadata in app.stream(
                    {
                        "messages": [
                            HumanMessage(content=user_input)
                        ]
                    },
                    config=config,
                    stream_mode="messages"
                ):

                    if isinstance(chunk, AIMessageChunk):

                        if isinstance(chunk.content, str):

                            if chunk.content:
                                yield chunk.content

                        elif isinstance(chunk.content, list):

                            for block in chunk.content:

                                if (
                                    isinstance(block, dict)
                                    and block.get("type") == "text"
                                ):
                                    text = block.get("text", "")

                                    if text:
                                        yield text

            # Display streaming response
            ai_res = st.write_stream(stream_response())

        # Save complete AI response
        st.session_state.message_history.append({
            "role": "assistant",
            "content": ai_res
        })