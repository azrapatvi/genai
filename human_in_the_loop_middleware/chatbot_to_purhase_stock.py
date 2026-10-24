
# ============================================================
# Stock Trading Chatbot with Human-in-the-Loop using LangGraph
# ============================================================
#
# This chatbot demonstrates the Human-in-the-Loop (HITL) concept
# using LangGraph and Groq LLM.
#
# Features:
# 1. Fetches the latest stock prices using Alpha Vantage API.
# 2. Allows users to request stock purchases.
# 3. Pauses graph execution using interrupt() before purchasing.
# 4. Asks for human approval (Yes/No).
# 5. Resumes execution using Command(resume=decision).
# 6. Uses InMemorySaver to maintain graph state during interrupts.
#
# Note: Stock purchasing is simulated. No real transactions occur.
# ============================================================


import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain.messages import SystemMessage
from langgraph.graph import StateGraph, START,END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from langchain.messages import AIMessage,HumanMessage,SystemMessage
import requests

load_dotenv()



#tools creation
@tool
def get_stock_prices(symbol:str):
    """a tool to get the stock prices .this will fetch latest stock prices for a given symbole (e.g AAPL,TSLA)"""
    url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=F6JN9MU7CLDCVM28"

    r=requests.get(url)

    return r.json()

@tool
def purchase_stock(symbol:str,quantity:int):
    """responsible for purchasing the stock of the given symbols based upon the quantity given.before confirming the purchase, this toll qill interrupt the exxecution and will ask the human for decision of whether to purchase or not"""

    decision=interrupt({
        "question":f"Approve the purchase of {quantity} shares of {symbol}?",
        "options":['yes','no']
    })
    if decision.lower().strip()=='yes':
        return {
            "status":"success",
            "message":f"Approved the purchase of {quantity} shares of {symbol}.",
            "symbol":symbol,
            "quantity":quantity
        }
    else:
        return {
            "status":"cancelled",
            "message":f"The purchase of {quantity} shares of {symbol} is declined by the human.",
            "symbol":symbol,
            "quantity":quantity
        }


def build_chatbot():

    #llm creation
    llm = ChatGroq(model="openai/gpt-oss-120b")

    #bind tools together
    tools = [get_stock_prices, purchase_stock]
    llm_with_tools=llm.bind_tools(tools)

    #State Creation
    class State(TypedDict):
        messages:Annotated[list,add_messages]

    #graph building
    builder=StateGraph(State)

    #cdefining chatbot node functionality
    def chatbot(state:State):
        return {
            "messages":[llm_with_tools.invoke(state['messages'])]
        }

    builder.add_node('chatbot',chatbot)
    builder.add_node('tools',ToolNode(tools))

    builder.add_edge(START,'chatbot')
    builder.add_conditional_edges('chatbot',tools_condition)
    builder.add_edge('tools','chatbot')

    memory=InMemorySaver()
    #compile the grpah
    graph=builder.compile(checkpointer=memory)

    return graph



if __name__=='__main__':
    while True:
        

        user_input=input("\nyou: ")
        if user_input.lower().strip()=='exit':
            break
        else:
            bot=build_chatbot()

            config1={'configurable':{'thread_id':"chat1"}}

            response=bot.invoke({"messages":user_input},config=config1)

            while response.get('__interrupt__'):
                interrupt_data = response["__interrupt__"][0].value

                print("\nHUMAN APPROVAL REQUIRED")
                print(interrupt_data["question"])

                decision = input("Your decision (yes/no): ").lower().strip()

                while decision not in ["yes", "no"]:
                    decision = input("Please enter yes or no: ").lower().strip()

                if decision.lower().strip()=='yes':
                    response=bot.invoke(Command(resume=decision),config=config1)

            # Final chatbot response
            print("\nBot:", response["messages"][-1].content)


