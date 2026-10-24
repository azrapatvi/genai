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

from core.vector_store import get_embeddings,build_vector_store,get_retriever,load_vector_store
load_dotenv()

def get_llm():
    return ChatGroq(model='openai/gpt-oss-120b')

# Convert retrieved documents into one text string
def format_docs(docs):
    return "\n\n".join(
        doc.page_content for doc in docs
    )




# Build the RAG chain
def build_rag_chain(transcribe:str):
    llm=get_llm()
    vector_store=build_vector_store(transcribe)
    retriever = get_retriever(vector_store, k=4)

    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system","""
    You are a helpful video assistant.

    Answer the user's question using only the context below.

    If the answer is not available in the context,
    say that the information was not found in the video transcript.

    Context:
    {context}


    Answer:
    """),
    ("human","{question}")])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    vector_store = load_vector_store()
    retriver = get_retriever(vector_store, k=4)

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context":  retriver| RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

def ask_question(rag_chain,question):
    print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    print(f"answer :{answer}")
    return answer