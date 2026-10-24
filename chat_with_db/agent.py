
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

DB_URI = "sqlite:///E:/chatbot/chat_with_db/student.db"

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# Main database connection: discover available tables
db = SQLDatabase.from_uri(DB_URI)

def get_table_agent(table_name):

    # Only expose the selected table to the SQL toolkit
    selected_db = SQLDatabase.from_uri(
        DB_URI,
        include_tables=[table_name]
    )

    selected_agent = create_sql_agent(
        llm=llm,
        db=selected_db,
        agent_type="tool-calling",
        verbose=True,
        prefix=f"""
        You are a helpful SQL database assistant.

        The user has selected the table: {table_name}.

        Rules:
        - Answer questions using ONLY the selected table.
        - Do not use other tables.
        - Use SQL tools to inspect the schema when necessary.
        - Never invent database results.
        - Never INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE anything.
        - Explain your answers clearly and simply.

        You have access to tools for interacting with a SQL database.
        """
    )

    return selected_agent
