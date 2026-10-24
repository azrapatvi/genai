import html

import pandas as pd
import streamlit as st
from sqlalchemy import text, inspect

from agent import db, get_table_agent


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SQL AI Explorer",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #F8FAFC;
}

#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263244;
}

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 6rem;
}

.hero {
    padding: 28px 32px;
    border-radius: 18px;
    background: linear-gradient(120deg, #123B47, #14243E);
    border: 1px solid #28566B;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 34px;
    margin: 0;
    padding: 0;
}

.hero p {
    color: #B9CBD7;
    margin-top: 10px;
    margin-bottom: 0;
}

.metric-card {
    background: #151F30;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #29374B;
    border-left: 3px solid #2DD4BF;
    margin-bottom: 18px;
    min-height: 105px;
}

.metric-title {
    color: #94A3B8;
    font-size: 14px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 29px;
    font-weight: 700;
    margin-top: 8px;
}

.section-title {
    font-size: 22px;
    font-weight: 650;
    margin-top: 12px;
    margin-bottom: 8px;
}

.table-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    background: rgba(45, 212, 191, .12);
    border: 1px solid rgba(45, 212, 191, .35);
    color: #2DD4BF;
    font-size: 15px;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #34465A;
    min-height: 42px;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    border-color: #2DD4BF;
    color: #2DD4BF;
}

[data-testid="stChatMessage"] {
    border-radius: 12px;
    border: 1px solid #263448;
    background: #151F30;
    padding: 12px;
    margin-bottom: 10px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #29374B;
    border-radius: 12px;
}

/* Keep the native bottom bar; only match the theme.
   Do NOT set position/left/right/width on stBottom or stChatInput. */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: #0B1120 !important;
}

@media (max-width: 768px) {
    .hero { padding: 20px; }
    .hero h1 { font-size: 27px; }
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 6rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

st.session_state.setdefault("chat_history", {})
st.session_state.setdefault("pending_question", None)


# ==========================================
# LOAD TABLES
# ==========================================

tables = db.get_usable_table_names()

if not tables:
    st.error("No tables found in your database.")
    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("SQL AI Explorer")
    st.caption("Intelligent Database Assistant")

    st.divider()

    st.success("Database Connected")

    st.subheader("Database Explorer")

    selected_table = st.selectbox(
        "Select a table",
        options=tables,
        key="selected_table",
    )

    st.caption(f"{len(tables)} table(s) available")

    st.divider()

    st.subheader("Selected Table")
    st.info(f"📋 {selected_table}")

    st.caption("Powered by LangChain + Groq + SQLite")

    st.divider()

    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        st.session_state.chat_history[selected_table] = []
        st.session_state.pending_question = None
        st.rerun()


# ==========================================
# CHAT HISTORY + AGENT
# ==========================================

messages = st.session_state.chat_history.setdefault(selected_table, [])


@st.cache_resource(show_spinner=False)
def load_agent(table_name):
    return get_table_agent(table_name)


agent = load_agent(selected_table)


# ==========================================
# TABLE STATISTICS
# ==========================================

engine = db._engine
inspector = inspect(engine)
safe_table = engine.dialect.identifier_preparer.quote(selected_table)

with engine.connect() as connection:
    total_rows = connection.execute(
        text(f"SELECT COUNT(*) FROM {safe_table}")
    ).scalar_one()

    preview_df = pd.read_sql_query(
        text(f"SELECT * FROM {safe_table} LIMIT 10"),
        connection,
    )

columns = inspector.get_columns(selected_table)
column_count = len(columns)
safe_name = html.escape(selected_table)


# ==========================================
# HERO SECTION
# ==========================================

st.markdown("""
<div class="hero">
    <h1>Chat With Your Database</h1>
    <p>
        Explore your SQL data using natural language.
        Select a table, ask questions, and get AI-powered answers.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# DASHBOARD CARDS
# ==========================================

col1, col2, col3 = st.columns(3)

for col, title, value in [
    (col1, "Available Tables", f"{len(tables)}"),
    (col2, "Rows in Selected Table", f"{total_rows:,}"),
    (col3, "Total Columns", f"{column_count}"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# CHAT INPUT
# Called before the tabs so the question can be
# answered inside the chat tab (no st.rerun needed).
# Streamlit still pins it to the bottom of the page.
# ==========================================

typed_question = st.chat_input(
    f"Ask anything about {selected_table}...",
    key=f"chat_input_{selected_table}",
)

question = typed_question or st.session_state.pending_question
st.session_state.pending_question = None


# ==========================================
# TABS
# ==========================================

tab1, tab2 = st.tabs(["💬 AI Chat Assistant", "📊 Table Preview"])


# ==========================================
# CHAT TAB
# ==========================================

with tab1:

    st.markdown(
        f'<div class="section-title">Ask about: '
        f'<span class="table-pill">{safe_name}</span></div>',
        unsafe_allow_html=True,
    )

    st.caption(f"The assistant is focused on the '{selected_table}' table.")

    # Suggested questions (only for an empty chat)
    if not messages and not question:

        st.write("### Try asking")

        suggestions = [
            f"How many records are in {selected_table}?",
            f"Show the first 5 records from {selected_table}.",
            f"What columns are available in {selected_table}?",
            f"Give me a summary of {selected_table}.",
        ]

        col_a, col_b = st.columns(2)

        for i, suggestion in enumerate(suggestions):
            with (col_a if i % 2 == 0 else col_b):
                if st.button(
                    suggestion,
                    key=f"suggestion_{selected_table}_{i}",
                    use_container_width=True,
                ):
                    st.session_state.pending_question = suggestion
                    st.rerun()

    # Previous messages
    for message in messages:
        with st.chat_message(
            message["role"],
            avatar="🧑" if message["role"] == "user" else "🤖",
        ):
            st.markdown(message["content"])

    # New question: shown and answered right here
    if question:

        messages.append({"role": "user", "content": question})

        with st.chat_message("user", avatar="🧑"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing your database..."):
                try:
                    result = agent.invoke({"input": question})
                    answer = str(result.get("output", result))
                except Exception as e:
                    answer = f"⚠️ An error occurred: {e}"

            st.markdown(answer)

        messages.append({"role": "assistant", "content": answer})


# ==========================================
# TABLE PREVIEW TAB
# ==========================================

with tab2:

    st.markdown(
        f'<div class="section-title">Table Preview: '
        f'<span class="table-pill">{safe_name}</span></div>',
        unsafe_allow_html=True,
    )

    st.caption("Displaying the first 10 records.")

    st.dataframe(preview_df, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Column Information")

    column_info = pd.DataFrame([
        {
            "Column Name": c["name"],
            "Data Type": str(c["type"]),
            "Nullable": c.get("nullable", True),
        }
        for c in columns
    ])

    st.dataframe(column_info, use_container_width=True, hide_index=True)