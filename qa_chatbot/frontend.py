import streamlit as st
from backend import create_app
from langchain.messages import HumanMessage


# ---------- DESIGN ONLY: page config + CSS ----------
st.set_page_config(page_title="AI Chat", page_icon="✨", layout="centered")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Same dark indigo / pink theme */
.stApp {
    background:
        radial-gradient(900px 500px at 10% -10%, rgba(99,102,241,.20), transparent 60%),
        radial-gradient(800px 500px at 100% 0%, rgba(236,72,153,.13), transparent 60%),
        #0b0d17;
    color: #e8eaf6;
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.6rem; padding-bottom: 6rem; max-width: 800px; }

/* Compact left-aligned header */
.top {
    display: flex; align-items: center; gap: 14px;
    padding-bottom: 1rem; margin-bottom: 1.6rem;
    border-bottom: 1px solid rgba(255,255,255,.08);
}
.top .logo {
    width: 40px; height: 40px; border-radius: 12px; display: grid; place-items: center;
    font-size: 18px; background: linear-gradient(135deg, #6366f1, #ec4899);
}
.top h1 { font-size: 1.2rem; font-weight: 600; margin: 0; color: #f1f2fb; letter-spacing: -.01em; }
.top p { margin: 0; font-size: .82rem; color: #8f98c0; }

/* Messages: AI left, you right */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 4px 16px 16px 16px;
    padding: .8rem 1.1rem;
    margin-bottom: .9rem;
    width: fit-content;
    max-width: 88%;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    margin-left: auto;
    flex-direction: row-reverse;
    background: linear-gradient(135deg, rgba(99,102,241,.40), rgba(168,85,247,.30));
    border-color: rgba(129,140,248,.40);
    border-radius: 16px 4px 16px 16px;
}
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessageAvatarUser"] { display: none; }
[data-testid="stChatMessage"] p { line-height: 1.7; font-size: 15.5px; color: #e8eaf6; }
[data-testid="stChatMessage"] code { background: #12142a; color: #c7d2fe; border-radius: 5px; padding: 1px 6px; }
[data-testid="stChatMessage"] pre { background: #12142a !important; border: 1px solid rgba(255,255,255,.08); border-radius: 10px; }

/* Input */
[data-testid="stBottom"] > div { background: transparent; }
[data-testid="stChatInput"] {
    background: rgba(18,20,36,.9);
    border: 1px solid rgba(129,140,248,.30);
    border-radius: 14px;
}
[data-testid="stChatInput"] textarea { color: #e8eaf6; }
[data-testid="stChatInput"]:focus-within {
    border-color: #a5b4fc;
    box-shadow: 0 0 0 3px rgba(129,140,248,.20);
}
[data-testid="stChatInput"] button { background: linear-gradient(135deg, #6366f1, #a855f7); color: #fff; border-radius: 10px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(12,14,26,.95);
    border-right: 1px solid rgba(255,255,255,.07);
}
[data-testid="stSidebar"] label p { font-size: 13px; color: #8f98c0; }
.stTextInput input {
    background: rgba(255,255,255,.05) !important; color: #e8eaf6 !important;
    border: 1px solid rgba(255,255,255,.12) !important; border-radius: 10px !important;
}
.stTextInput input:focus { border-color: #818cf8 !important; }

[data-testid="stAlert"] { border-radius: 12px; }

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: rgba(129,140,248,.30); border-radius: 8px; }
</style>

<div class="top">
    <div class="logo">✨</div>
    <div>
        <h1>AI Chat</h1>
        <p>Ask anything, get quick answers</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
# ---------- END DESIGN ----------


groq_api_key = st.sidebar.text_input(
    "Enter GROQ API Key:", type="password"
)
if not groq_api_key:
    st.warning("Please enter your API key.")
    st.stop()


chat_thread_id = st.sidebar.text_input(
    "Chat Session ID", value="chat1"
)
if not chat_thread_id:
    st.warning("Enter a chat session ID.")
    st.stop()


# Create app only once
if "app" not in st.session_state:
    st.session_state.app = create_app(groq_api_key)

app = st.session_state.app


if "message_history" not in st.session_state:
    st.session_state.message_history = []

# to load the hsitory messages
for message in st.session_state.message_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_input = st.chat_input("Type here...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    config = {"configurable": {"thread_id": chat_thread_id}}

    response = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )

    ai_res = response["messages"][-1].content

    with st.chat_message("assistant"):
        st.write(ai_res)

    st.session_state.message_history.append(
        {"role": "user", "content": user_input}
    )
    st.session_state.message_history.append(
        {"role": "assistant", "content": ai_res}
    )