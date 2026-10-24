import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph,START,END
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_groq import ChatGroq
import sqlite3

load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")
list_of_threads=set()
def create_app(groq_api_key):
    llm=ChatGroq(model='openai/gpt-oss-120b',api_key=groq_api_key)


    #state defining
    class State(TypedDict):
        messages:Annotated[list,add_messages]

    #building graph
    graph_builder=StateGraph(State)

    #chatbot node
    def chatbot(state:State):
        """a chatbot to comunicate"""
        response = llm.invoke(state["messages"][-6:])

        return {
            "messages": [response]
        }

    # adding node
    graph_builder.add_node("llm_chatbot",chatbot)

    # adding edges
    graph_builder.add_edge(START,"llm_chatbot")
    graph_builder.add_edge("llm_chatbot",END)

    conn=sqlite3.connect(
        'chatbot_with_db.db',
        check_same_thread=False
    )
    memory=SqliteSaver(conn=conn)
    app=graph_builder.compile(checkpointer=memory)

    
    
    for checkpoint in memory.list(None):
        print(checkpoint.config['configurable']['thread_id'])
        list_of_threads.add(checkpoint.config['configurable']['thread_id'])
    
    print(list_of_threads)

    return app

create_app(groq_api_key)