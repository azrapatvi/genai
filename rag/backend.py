
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
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

# Load the embedding model once
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def create_pdf_graph(pdf_path: str):
    # 1. Load the uploaded PDF
    loader = PyPDFLoader(pdf_path)
    data = loader.load()

    # 2. Split the PDF into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    splitted_data = splitter.split_documents(data)

    if not splitted_data:
        raise ValueError("The PDF contains no readable text.")

    # 3. Create a vector store for this PDF
    vector_store = FAISS.from_documents(
        splitted_data,
        embedding=embeddings
    )

    # 4. Create the retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
    )

    # 5. Create the RAG tool
    @tool
    def rag_tool(query: str) -> str:
        """Search the uploaded PDF and return relevant information with page numbers."""

        docs = retriever.invoke(query)

        if not docs:
            return "No relevant information was found in the PDF."

        results = []

        for doc in docs:
            page = doc.metadata.get("page", 0) + 1
            source = doc.metadata.get("source", "Uploaded PDF")

            results.append(
                f"Source: {os.path.basename(source)}, "
                f"Page: {page}\n"
                f"Content: {doc.page_content}"
            )

        return "\n\n".join(results)

    tools = [rag_tool]

    llm_with_tool = llm.bind_tools(tools)

    # 6. Define the chatbot node
    def chatbot(state: State):
        system_message = SystemMessage(
            content="""
            You are a PDF question-answering assistant.

            Always use rag_tool to answer questions about the uploaded PDF.
            Base your answers on the retrieved document content.
            If the document does not contain the answer, clearly say so.
            Do not invent facts or page references.
            Include the source page numbers when available.
            """
        )

        response = llm_with_tool.invoke(
            [system_message] + state["messages"]
        )

        return {"messages": [response]}

    # 7. Build the LangGraph workflow
    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools))

    graph_builder.add_edge(START, "chatbot")

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )

    graph_builder.add_edge("tools", "chatbot")

    # 8. Add conversation memory
    memory = InMemorySaver()

    graph = graph_builder.compile(
        checkpointer=memory
    )

    return graph
