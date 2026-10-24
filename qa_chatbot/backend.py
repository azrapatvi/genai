import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph,START,END
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_groq import ChatGroq


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

    memory=MemorySaver()
    app=graph_builder.compile(checkpointer=memory)

    return app