
from pathlib import Path

import streamlit as st

from main import run_pipeline
from core.rag_engine import ask_question


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Vidi AI | Video Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0b0d17;
    --panel: #121626;
    --border: #262b40;
    --muted: #9ba3bd;
    --purple: #a78bfa;
    --blue: #60a5fa;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #1c1740 0%, transparent 34%),
        radial-gradient(ellipse at 95% 10%, #102747 0%, transparent 30%),
        #0b0d17;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0e1120;
    border-right: 1px solid #262b40;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.8rem;
}

h1, h2, h3, p, label {
    font-family: 'Inter', sans-serif;
}

h1 {
    letter-spacing: -1.6px;
    font-weight: 800 !important;
}

h2, h3 {
    letter-spacing: -0.5px;
}

.hero {
    padding: 30px 32px;
    border: 1px solid #343254;
    border-radius: 24px;
    background: linear-gradient(
        125deg,
        rgba(94, 62, 180, 0.25),
        rgba(22, 42, 78, 0.35),
        rgba(18, 22, 38, 0.9)
    );
    margin-bottom: 26px;
}

.eyebrow {
    color: #c4b5fd;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-size: clamp(30px, 4vw, 48px);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -2px;
    margin: 14px 0;
    color: #f5f3ff;
}

.gradient-text {
    background: linear-gradient(90deg, #c4b5fd, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    color: #b5bdd2;
    font-size: 15px;
    line-height: 1.8;
    max-width: 680px;
}

.panel {
    background: rgba(18, 22, 38, 0.88);
    border: 1px solid #282d43;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
}

.stat-card {
    background: linear-gradient(145deg, #171b30, #111524);
    border: 1px solid #2b3048;
    border-radius: 16px;
    padding: 20px;
    min-height: 115px;
}

.stat-label {
    color: #9ba3bd;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stat-value {
    color: #f3f4ff;
    font-size: 25px;
    font-weight: 800;
    margin-top: 12px;
    overflow-wrap: anywhere;
}

.section-label {
    color: #c4b5fd;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.muted {
    color: #9ba3bd;
    line-height: 1.7;
}

.stButton > button {
    border-radius: 10px;
    min-height: 44px;
    font-weight: 700;
    border: 1px solid #39325d;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #7c3aed, #4f70e8);
    color: white;
    border: none;
}

.stButton > button:hover {
    border-color: #a78bfa;
    transform: translateY(-1px);
}

.stTextInput input, .stTextArea textarea {
    background: #111524;
    border-color: #343a54;
    border-radius: 10px;
}

[data-baseweb="select"] > div {
    background: #111524;
    border-color: #343a54;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #292e44;
}

.stTabs [data-baseweb="tab"] {
    background: #121626;
    border-radius: 9px 9px 0 0;
    padding: 12px 16px;
}

.stTabs [aria-selected="true"] {
    color: #c4b5fd !important;
    border-bottom: 2px solid #a78bfa !important;
}

[data-testid="stFileUploader"] {
    background: #111524;
    border: 1px dashed #4b456f;
    border-radius: 12px;
    padding: 10px;
}

[data-testid="stChatMessage"] {
    background: rgba(20, 25, 43, 0.9);
    border: 1px solid #292e44;
    border-radius: 14px;
    padding: 12px;
}

[data-testid="stChatInput"] textarea {
    background: #111524;
}

hr {
    border-color: #292e44;
}

.footer {
    text-align: center;
    color: #737d99;
    font-size: 12px;
    padding: 30px 0 5px;
}

@media (max-width: 700px) {
    .hero {
        padding: 22px;
    }
    .hero-title {
        letter-spacing: -1px;
    }
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "video_name" not in st.session_state:
    st.session_state.video_name = ""


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;">
        <div style="
            background:linear-gradient(135deg,#8b5cf6,#3b82f6);
            border-radius:12px;
            width:46px;height:46px;
            display:flex;align-items:center;
            justify-content:center;font-size:24px;">
            🎬
        </div>
        <div>
            <div style="font-size:21px;font-weight:800;color:#f5f3ff;">
                Vidi AI
            </div>
            <div style="font-size:11px;color:#9ba3bd;">
                VIDEO INTELLIGENCE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Create a workspace")
    st.caption("Choose a video to start extracting insights.")

    with st.form("video_form"):
        youtube_url = st.text_input(
            "YouTube link",
            placeholder="Paste your video URL...",
        )

        uploaded_file = st.file_uploader(
            "Or upload a media file",
            type=[
                "mp4", "mkv", "mov", "avi",
                "mp3", "wav", "m4a", "webm"
            ],
        )

        language_choice = st.selectbox(
            "Transcript language",
            ["English", "Hinglish"],
        )

        process_button = st.form_submit_button(
            "✦  Analyze video",
            type="primary",
            use_container_width=True,
        )

    st.divider()

    st.markdown("#### YOUR WORKSPACE")

    if st.session_state.result:
        st.markdown("🟢  Analysis complete")
        st.caption(st.session_state.video_name or "Current video")
    else:
        st.markdown("⚪  No video analyzed yet")
        st.caption("Your insights will appear here.")

    st.divider()

    if st.button("↻  Clear current session", use_container_width=True):
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.video_name = ""
        st.rerun()

    st.markdown("""
    <div style="margin-top:30px;color:#737d99;font-size:11px;line-height:1.8;">
        POWERED BY<br>
        <span style="color:#c4b5fd;font-weight:700;">
            AI · RAG · VECTOR SEARCH
        </span>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# HERO
# ==================================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">✦ YOUR PERSONAL VIDEO INTELLIGENCE</div>
    <div class="hero-title">
        Every video has insights.<br>
        <span class="gradient-text">Let's find them.</span>
    </div>
    <div class="hero-description">
        Turn long videos into clear summaries, actionable tasks and key
        decisions. Then ask questions and get answers grounded in the
        video transcript.
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# PROCESS VIDEO
# ==================================================

if process_button:
    if not youtube_url.strip() and uploaded_file is None:
        st.error("Please paste a YouTube link or upload a media file.")

    else:
        source = youtube_url.strip()

        if not source:
            upload_folder = Path("uploaded_videos")
            upload_folder.mkdir(parents=True, exist_ok=True)

            file_path = upload_folder / Path(uploaded_file.name).name
            file_path.write_bytes(uploaded_file.getvalue())
            source = str(file_path.resolve())

        language = "en" if language_choice == "English" else "hi"

        try:
            with st.spinner(
                "Analyzing your video... Transcribing, summarizing "
                "and extracting insights."
            ):
                result = run_pipeline(source, language)

            st.session_state.result = result
            st.session_state.chat_history = []
            st.session_state.video_name = (
                result.get("title") or Path(source).name
            )

            st.success("Your video insights are ready!")

        except Exception as error:
            st.error(f"Video processing failed: {error}")


# ==================================================
# RESULTS
# ==================================================

result = st.session_state.result

if result:
    st.markdown('<div class="section-label">YOUR ANALYSIS</div>',
                unsafe_allow_html=True)

    st.markdown(f"## {result['title']}")

    st.markdown(
        '<p class="muted">Here is what we discovered from your video.</p>',
        unsafe_allow_html=True,
    )

    # Overview cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">✦ Overview</div>
            <div class="stat-value">Summary</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">✓ Productivity</div>
            <div class="stat-value">Action Items</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">⌘ Knowledge</div>
            <div class="stat-value">Decisions</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    summary_tab, actions_tab, decisions_tab, questions_tab, transcript_tab = (
        st.tabs([
            "✦  Summary",
            "✓  Action Items",
            "◆  Key Decisions",
            "?  Open Questions",
            "≡  Transcript",
        ])
    )

    with summary_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Video at a glance")
        st.markdown(result["summary"])
        st.markdown('</div>', unsafe_allow_html=True)

    with actions_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### What needs to be done?")
        st.markdown(result["action_items"])
        st.markdown('</div>', unsafe_allow_html=True)

    with decisions_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Important decisions")
        st.markdown(result["key_decisions"])
        st.markdown('</div>', unsafe_allow_html=True)

    with questions_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Questions to revisit")
        st.markdown(result["open_questions"])
        st.markdown('</div>', unsafe_allow_html=True)

    with transcript_tab:
        st.markdown("### Full transcript")

        st.text_area(
            "Transcript",
            value=result["transcript"],
            height=350,
            disabled=True,
            label_visibility="collapsed",
        )

        st.download_button(
            "↓  Download transcript",
            data=result["transcript"],
            file_name="video_transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ==================================================
    # CHAT WITH VIDEO
    # ==================================================

    st.write("")
    st.divider()

    st.markdown('<div class="section-label">AI ASSISTANT</div>',
                unsafe_allow_html=True)
    st.markdown("## Ask your video anything")
    st.markdown(
        '<p class="muted">Ask for explanations, important details, '
        'decisions or specific information mentioned in the video.</p>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### 💬 Video conversation")

        if not st.session_state.chat_history:
            st.markdown("""
            <div style="
                padding:16px;
                background:#111524;
                border:1px solid #292e44;
                border-radius:12px;
                margin-bottom:16px;">
                <div style="font-weight:700;color:#c4b5fd;">
                    Ready when you are
                </div>
                <div style="color:#9ba3bd;font-size:13px;margin-top:6px;">
                    Try asking what the video is about, what the main
                    conclusions are, or which actions were suggested.
                </div>
            </div>
            """, unsafe_allow_html=True)

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input(
            "Ask a question about your video..."
        )

        if question:
            st.session_state.chat_history.append({
                "role": "user",
                "content": question,
            })

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Searching the transcript..."):
                    try:
                        answer = ask_question(
                            result["rag_chain"],
                            question,
                        )

                        st.markdown(answer)

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": str(answer),
                        })

                    except Exception as error:
                        st.error(f"Could not generate an answer: {error}")

else:
    # Empty state before the first video
    st.markdown('<div class="section-label">HOW IT WORKS</div>',
                unsafe_allow_html=True)
    st.markdown("## From video to understanding")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="panel">
            <div style="font-size:28px;">🎧</div>
            <h3>01 · Transcribe</h3>
            <p class="muted">
                Convert video or audio into text that can be searched
                and analyzed.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="panel">
            <div style="font-size:28px;">✦</div>
            <h3>02 · Extract insights</h3>
            <p class="muted">
                Generate a summary, identify decisions and discover
                important action items.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="panel">
            <div style="font-size:28px;">💬</div>
            <h3>03 · Ask questions</h3>
            <p class="muted">
                Chat with the transcript using retrieval-augmented
                generation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "To begin, paste a YouTube link or upload a video using "
        "the sidebar, then select **Analyze video**."
    )


# ==================================================
# FOOTER
# ==================================================

st.markdown("""
<div class="footer">
    Vidi AI · Video intelligence, simplified.
</div>
""", unsafe_allow_html=True)
