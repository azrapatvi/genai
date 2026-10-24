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
def llm():
    llm=ChatGroq(model='openai/gpt-oss-120b')
    return llm


# text_splitter
def split_transcript(transcript:str)->list:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=500
    )
    text=splitter.split_text(transcript)
    return text


def summarize(transcript: str):
    model = llm()

    map_prompt=ChatPromptTemplate.from_messages([
        ("system","you are an expert summarizer , sumarize the text which is given to you"),
        ("human","{text}")
    ])

    map_chain=map_prompt|model|StrOutputParser()

    chunks=split_transcript(transcript)
    chunk_summaries=[map_chain.invoke({'text':chunk}) for chunk in chunks]

    combined="\n\n".join(chunk_summaries)

    #so here we will get summarization of the chunks so there might ahppenn that some part in summarization aloss gets repeated

    
    combined_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert meeting summarizer.
    Combine these partial summaries into one final professional
    meeting summary in bullet points."""),
        ("human", "{text}")
    ])


    
    combined_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | combined_prompt
        | model
        | StrOutputParser()
    )


    return combined_chain.invoke(combined)


def get_title(transcribe: str):
    model = llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Based on the video transcript, generate a short professional title
(maximum 8 words). Return only the title, nothing else."""),
        ("human", "{text}")
    ])

    chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | prompt
        | model
        | StrOutputParser()
    )

    return chain.invoke(transcribe)



    