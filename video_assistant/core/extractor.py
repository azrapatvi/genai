from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


# llm creation
def get_llm():
    llm=ChatGroq(model='openai/gpt-oss-120b')
    return llm

#this funciton is for so that we dont need to reate the chain againa nd again...we just can change the prompt and it will update it in the sytem
def build_chain(system_prompt:str):
    llm=get_llm()
    prompt=ChatPromptTemplate.from_messages([   # CHANGED: from_template -> from_messages (zaroori, warna error aayega)
        ("system",system_prompt),
        ("human","{text}")
    ])
    chain=RunnablePassthrough()|RunnableLambda(lambda x:{'text':x})|prompt|llm|StrOutputParser()

    return chain

splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)

def extract_action_items(transcript:str):
    chain=build_chain("You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'")
    parts=splitter.split_text(transcript)
    results=[chain.invoke(chunk) for chunk in parts]

    merge_chain = build_chain("Merge these lists into one, remove duplicates, keep numbering.")
    return merge_chain.invoke("\n\n".join(results))

def key_decisions(transcript:str):
    chain=build_chain("You are an expert meeting analyst. From the meeting transcript, "
    "extract all key decisions made. Format as a numbered list. "
    "If none found say 'No key decisions found. '")
    parts=splitter.split_text(transcript)
    results=[chain.invoke(chunk) for chunk in parts]
    
    merge_chain = build_chain("Merge these lists into one, remove duplicates, keep numbering.")
    return merge_chain.invoke("\n\n".join(results))

def extract_questions(transcript:str):
    chain=build_chain("From the meeting transcript, extract all unresolved questions "   # CHANGED: "questions " (s + space)
    "or topics needing follow-up. Format as a numbered list. "                           # CHANGED: trailing space
    "If none found say 'No open questions found. '")
    parts=splitter.split_text(transcript)
    results=[chain.invoke(chunk) for chunk in parts]
    
    merge_chain = build_chain("Merge these lists into one, remove duplicates, keep numbering.")
    return merge_chain.invoke("\n\n".join(results))