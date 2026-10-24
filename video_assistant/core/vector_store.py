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
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
load_dotenv()

MODEL_NAME='all-MiniLM-L6-v2'
COLLECTION_NAME='VIDEO-ASSISTANT'
PERSIST_DIRECTORY='./chroma-db'

def get_embeddings():
    embeddings=HuggingFaceEmbeddings(model_name=MODEL_NAME)
    return embeddings

def build_vector_store(transcribe:str):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200
    )
    chunks=splitter.split_text(transcribe)

    docs = []

    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={'chunk_index': i}
        )
        docs.append(doc)

    embeddings=get_embeddings()
    vector_store=Chroma.from_documents(
        docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY
    )
    return vector_store

def load_vector_store() ->Chroma:
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function= embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

    return vector_store
def get_retriever(vector_store:Chroma,k:int=4):
    return vector_store.as_retriever(search_kwargs={'k':k})
