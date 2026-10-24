import streamlit as st
import json
import sqlite3

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from pydantic import BaseModel, Field
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Movie Information Extractor",
    page_icon="🎬",
    layout="wide"
)


# ----------------------------------
# DATABASE
# ----------------------------------

conn = sqlite3.connect(r'E:\chatbot\cineSage\cinesage.db')
cursor = conn.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT,
            director TEXT,
            release_year INTEGER,
            genre TEXT,
            lead_actors TEXT,
            summary TEXT
        )
    """)

conn.commit()
print("Movies table created successfully!")
conn.close()


# ----------------------------------
# YOUR SAVE FUNCTION
# ----------------------------------
def save_details(res):

    conn = sqlite3.connect(r'E:\chatbot\cineSage\cinesage.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movies (
            movie_name,
            director,
            release_year,
            genre,
            lead_actors,
            summary
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        res['movie_name'],
        res['director'],
        res['release_year'],
        ", ".join(res['genre']) if isinstance(res['genre'], list) else res['genre'],
        json.dumps(res['lead_actors']),
        res['summary']
    ))

    conn.commit()
    print("Records inserted successfully!")
    conn.close()

# ----------------------------------
# YOUR PYDANTIC MODEL
# ----------------------------------

class MovieInfo(BaseModel):

    movie_name: Optional[str] = Field(
        description="Name of the movie"
    )

    director: Optional[str] = Field(
        description="Movie director"
    )

    release_year: Optional[int] = Field(
        description="Release year"
    )

    genre: Optional[list[str]] = Field(
        description="Movie genres"
    )

    lead_actors: Optional[list[str]] = Field(
        description="Lead actors"
    )

    summary: str = Field(
        description="Summary based only on the given paragraph"
    )

    missing_information: list[str] = Field(
        description="Requested details not provided in the paragraph"
    )


# ----------------------------------
# YOUR LLM
# ----------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# ----------------------------------
# YOUR EXISTING PROMPT
# ----------------------------------

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Movie Information Extraction Agent.

Your task is to read the movie paragraph provided by the user
and extract all relevant movie information, and summarize the paragraph.

Extract the following details:
1. movie_name
2. director
3. release_year
4. genre
5. lead_actors
6. give summary of the info

RULES:
- Extract information only from the given paragraph.
- Do not use external knowledge.
- Never invent missing information.
- if information is missing then ask for it but just dont invent anything on your own...
- use the attached formatted structure

{format_instructions}
"""),
    ("human", "{para}")
])


# ----------------------------------
# YOUR EXISTING OUTPUT PARSER
# ----------------------------------

parser = JsonOutputParser()

prompt = prompt.partial(
    format_instructions=parser.get_format_instructions()
)

chain = prompt | llm | parser


# ----------------------------------
# SESSION STATE
# ----------------------------------

if "movie_result" not in st.session_state:
    st.session_state.movie_result = None

if "movie_saved" not in st.session_state:
    st.session_state.movie_saved = False


# ----------------------------------
# STREAMLIT UI
# ----------------------------------

st.title("🎬 CineSage")
st.caption("AI-Powered Movie Information Extraction")

st.write(
    "Extract movie details and generate a summary "
    "from any movie paragraph using AI."
)

st.divider()

st.subheader("Enter Movie Paragraph")

user_input = st.text_area(
    "Paste your movie description below:",
    placeholder=(
        "Example: Inception is a 2010 science fiction "
        "film written and directed by Christopher Nolan..."
    ),
    height=220
)

extract_button = st.button(
    "Extract Movie Information",
    type="primary",
    use_container_width=True
)


# ----------------------------------
# RUN YOUR EXISTING CHAIN
# ----------------------------------

if extract_button:

    if not user_input.strip():
        st.warning("Please enter a movie paragraph first.")

    else:

        try:

            with st.spinner("Extracting movie information..."):

                res = chain.invoke({
                    "para": user_input
                })

            st.session_state.movie_result = res
            st.session_state.movie_saved = False

            st.success("Movie information extracted!")

        except Exception as e:

            st.session_state.movie_result = None

            st.error("Unable to extract movie information.")
            st.write("Error details:", str(e))


# ----------------------------------
# DISPLAY EXTRACTED INFORMATION
# ----------------------------------

if st.session_state.movie_result is not None:

    res = st.session_state.movie_result

    st.divider()

    st.subheader("Extracted Movie Details")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("**Movie Name**")
        st.write(res.get("movie_name") or "Not provided")

        st.markdown("**Director**")
        st.write(res.get("director") or "Not provided")

        st.markdown("**Release Year**")
        st.write(res.get("release_year") or "Not provided")

    with col2:

        st.markdown("**Genre**")

        genre = res.get("genre")

        st.write(
            ", ".join(genre) if isinstance(genre, list)
            else (genre or "Not provided")
        )

        st.markdown("**Lead Actors**")

        actors = res.get("lead_actors")

        st.write(
            ", ".join(actors) if actors else "Not provided"
        )

    # ----------------------------------
    # SUMMARY
    # ----------------------------------

    st.divider()

    st.subheader("Movie Summary")

    st.write(
        res.get("summary", "No summary available.")
    )

    # ----------------------------------
    # MISSING INFORMATION
    # ----------------------------------

    missing = res.get("missing_information", [])

    if missing:

        st.divider()

        st.subheader("Missing Information")

        st.info(
            "The paragraph does not provide all requested details."
        )

        for item in missing:
            st.write(f"- {item}")

    # ----------------------------------
    # JSON OUTPUT
    # ----------------------------------

    st.divider()

    with st.expander("View Complete JSON Output"):
        st.json(res)

    # ----------------------------------
    # DOWNLOAD JSON
    # ----------------------------------

    json_data = json.dumps(
        res,
        indent=4,
        ensure_ascii=False
    )

    st.download_button(
        label="Download JSON",
        data=json_data,
        file_name="movie_information.json",
        mime="application/json",
        use_container_width=True
    )

    # ----------------------------------
    # ADD INTO DATABASE
    # ----------------------------------

    st.divider()

    st.subheader("Save Movie Information")

    st.write(
        "Click the button below to save the extracted "
        "movie information into your SQLite database."
    )

    if st.button(
        "Add into DB",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.movie_saved
    ):

        try:

            save_details(res)

            st.session_state.movie_saved = True

            st.rerun()

        except Exception as e:

            st.error("Unable to save movie information.")
            st.write("Error details:", str(e))

    if st.session_state.movie_saved:

        st.success(
            "Movie details successfully added to the database!"
        )