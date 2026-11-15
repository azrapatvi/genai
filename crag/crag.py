import os
import tempfile

# ---- Vercel: only /tmp is writable, so point every cache there ----
# (must be set BEFORE importing fastembed / huggingface)
TMP = tempfile.gettempdir()
os.environ["HF_HOME"] = os.path.join(TMP, "hf")
os.environ["HF_HUB_CACHE"] = os.path.join(TMP, "hf", "hub")
os.environ["XDG_CACHE_HOME"] = TMP
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["FASTEMBED_CACHE_PATH"] = os.path.join(TMP, "fastembed")

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq

# PDF loading
from langchain_community.document_loaders import PyPDFLoader

# Text splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embeddings and vector database
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS

# Prompts and output parser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# Document chain
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain
)

from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv

load_dotenv()

# llm
llm = ChatGroq(model='openai/gpt-oss-120b')

# embeddings are loaded on first use (not at startup)
embeddings = None


def get_embeddings():
    global embeddings
    if embeddings is None:
        embeddings = FastEmbedEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_dir=os.path.join(TMP, "fastembed")
        )
    return embeddings


# retriever is created after the user uploads a PDF
retriever = None

def build_index(pdf_path):
    global retriever

    loader = PyPDFLoader(pdf_path)
    loaded_data = loader.load()
    print("PDF loaded successfully!")
    print("Total pages:", len(loaded_data))

    # split the documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splitted_text = splitter.split_documents(loaded_data)
    print("Data Splitted Successfully")

    vector = FAISS.from_documents(
        embedding=embeddings,
        documents=splitted_text
    )

    # create retriever
    retriever = vector.as_retriever(search_kwargs={"k": 8})
    print("FAISS database created successfully!")


# document grader
grade_prompt = ChatPromptTemplate.from_template("""
    You are a document relevance evaluator.

    User Question:
    {question}

    Retrieved Document:
    {document}

    Check whether the retrieved document contains
    information useful for answering the question.

    Strictly Reply with ONLY one word:
    "YES" or "NO" only.
""")

grade_chain = grade_prompt | llm | StrOutputParser()

rewrite_prompt = ChatPromptTemplate.from_template("""

You are a search query optimizer.

Rewrite the following user question into a
better search engine query.

Make it clear and specific.

Return ONLY the improved search query.

Question:
{question}

""")

rewrite_chain = rewrite_prompt | llm | StrOutputParser()

generation_prompt = ChatPromptTemplate.from_template("""

You are a helpful AI assistant.

Answer the question using ONLY the provided context.

If the answer is not available in the context,
clearly say that you don't have enough information to give answer based on the query.

Context:
{context}

Question:
{input}

Answer:

""")

document_chain = create_stuff_documents_chain(llm, generation_prompt)

contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", """
        Given the chat history and latest user question,
        rewrite the question as a standalone question.
        Do not answer the question.
        """),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])


def web_search(question):

    search = TavilySearchResults(max_results=5)
    results = search.invoke(question)

    web_documents = []

    for item in results:
        doc = Document(
            page_content=item.get('content'),
            metadata={
                'source': item.get('url')
            }
        )

        if doc.page_content.strip():
            web_documents.append(doc)

    return web_documents


chat_history = []   # simple memory
standalone_chain = contextualize_prompt | llm | StrOutputParser()


def crag(question):
    print("CRAG")

    # turn follow-ups like "who is she" into a full question
    if chat_history:
        search_question = standalone_chain.invoke({
            "input": question,
            "chat_history": chat_history
        })
        print("Standalone question:", search_question)
    else:
        search_question = question

    # retriever
    docs = retriever.invoke(search_question)

    print("Retrieved documents:", len(docs))

    relevant_docs = []

    for doc in docs:
        res = grade_chain.invoke({'question': search_question, 'document': doc.page_content})

        print("results are : ", res)
        result = res.strip().upper()

        print("Document grade:", result)

        if result.startswith("YES"):
            relevant_docs.append(doc)
            print("appended to relevant documents")

    if relevant_docs:

        print("\n. Relevant documents found!")
        print("Generating answer using PDF context...")

        answer = document_chain.invoke({
            'input': search_question,
            'context': relevant_docs
        })

        source = "PDF"

    else:

        print("\n. No relevant documents found!")

        improved_query = rewrite_chain.invoke({"question": search_question})
        print("Improved query:", improved_query)

        web_docs = web_search(improved_query)

        print("Web documents found:", len(web_docs))

        if web_docs:
            answer = document_chain.invoke({
                "input": search_question,
                "context": web_docs
            })

        else:

            answer = "No relevant web search results found."

        source = "WEB"

    # save memory so follow-ups work
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))

    return answer, source
