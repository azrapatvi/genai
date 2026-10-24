import os
from dotenv import load_dotenv
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# setting the api keys in enviornemnt
os.environ['LANGCHAIN_API_KEY']=os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_TRACING_V3'] = 'true'
os.environ['LANGCHAIN_PROJECT2']=os.getenv("LANGCHAIN_PROJECT2")


# create llm
llm=ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0
)

#prompt
prompt=ChatPromptTemplate.from_messages([
    ("system","you are a helpfull assistant"),
    ("user","{input}")
])

#parser
parser=StrOutputParser()

chain=prompt|llm|parser

st.title("LangChain + Ollama AI Chatbot")
st.write("Ask anything and get a response from a locally running AI model.")

text_input=st.text_input("hello what do you want to search")

if text_input:
    response=chain.invoke({"input":text_input})

    st.write(response)