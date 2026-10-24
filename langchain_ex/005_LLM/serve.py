import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from fastapi import FastAPI
from langserve import add_routes

# langserve converts your langchain application/chain into an api   
# so after this you will get POST /chain/invoke
# POST /chain/batch
# POST /chain/stream

# so the chain/invoke will call your chain through this api


load_dotenv()

# setting the api keys in enviornemnt
os.environ['LANGCHAIN_API_KEY']=os.getenv("LANGCHAIN_API_KEY")

# create llm
llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

#prompt template
prompt=ChatPromptTemplate.from_messages([
    ("system","you are an expert language translator; translate the following into {language}"),
    ("user","{input}")
])

#parser
parser=StrOutputParser()

#chain
chain=prompt|llm|parser

#app definataion
app=FastAPI(
    title="langchain server",
    version='1.0',
    description="simple API server using langchain serve"
)

add_routes(
    app,
    chain,
    path="/chain"
)
# without this you wont be able to get thosee api endpoints that directly created throguh lanserve


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host='localhost',port=8000)