
import streamlit as st
from backend import create_app
from langchain.messages import HumanMessage
import os
from dotenv import load_dotenv
import uuid

load_dotenv()


# Generate unique thread ID
def generate_threadi():
    return str(uuid.uuid4())


# Add thread ID to list
def add_thread_id(thread_id):
    if thread_id not in st.session_state.list_of_thread_id:
        st.session_state.list_of_thread_id.append(thread_id)


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


groq_api_key = os.getenv("GROQ_API_KEY")


# Initialize LangGraph app only once
if "app" not in st.session_state:
    st.session_state.app = create_app(groq_api_key)

app = st.session_state.app


# Initialize session states
if "list_of_thread_id" not in st.session_state:
    st.session_state.list_of_thread_id = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_threadi()

if "message_history" not in st.session_state:
    st.session_state.message_history = []


# Add current thread
add_thread_id(st.session_state.thread_id)


# SIDEBAR
st.sidebar.title("CHATBOT")


# New Chat Button
if st.sidebar.button("NEW CHAT"):

    # Generate new thread ID
    st.session_state.thread_id = generate_threadi()

    # Add new thread ID
    add_thread_id(st.session_state.thread_id)

    # Clear displayed messages
    st.session_state.message_history = []

    st.rerun()


# Conversation History
st.sidebar.title("Conversation History")


for thread_id in st.session_state.list_of_thread_id:

    if st.sidebar.button(
        thread_id,
        key=thread_id,
        use_container_width=True
    ):

        # Change current thread
        st.session_state.thread_id = thread_id

        # Load previous messages
        st.session_state.message_history = load_conversation(
            thread_id
        )

        st.rerun()


# MAIN CHAT INTERFACE
st.title("AI Chatbot")


# Display previous messages
for message in st.session_state.message_history:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# User Input
user_input = st.chat_input("Type here...")


if user_input:

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Save user message
    st.session_state.message_history.append({
        "role": "user",
        "content": user_input
    })

    # Current thread configuration
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    # STREAMING RESPONSE
    with st.chat_message("assistant"):

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

                # Stream AI-generated text
                if chunk.type == "AIMessageChunk":

                    if isinstance(chunk.content, str):
                        yield chunk.content

                    elif isinstance(chunk.content, list):

                        for block in chunk.content:

                            if (
                                isinstance(block, dict)
                                and block.get("type") == "text"
                            ):
                                yield block.get("text", "")

        # Display streaming response
        ai_res = st.write_stream(stream_response())

    # Save complete AI response
    st.session_state.message_history.append({
        "role": "assistant",
        "content": ai_res
    })
