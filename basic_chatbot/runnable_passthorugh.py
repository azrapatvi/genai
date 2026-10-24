from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel,RunnablePassthrough

load_dotenv()
os.environ['GROQ_API_KEY']=os.getenv('GROQ_API_KEY')

#llm creation
llm=ChatGroq(model='openai/gpt-oss-120b')

# prompts
generate_code_prompt=ChatPromptTemplate.from_messages([
    ("system","you are a code generator,so create a code for question"),
    ("human","{question}")
])

explain_code_prompt=ChatPromptTemplate.from_messages([
    ("system","you are a code explainer, so explain the provided code in simple english language"),
    ("human","explain this code {code}")
])

#output parser
parser=StrOutputParser()


#create a chain
seq1=generate_code_prompt|llm|parser

seq2=RunnableParallel({
    "code":RunnablePassthrough(),
    "explaination":explain_code_prompt|llm|parser
})

#so the code we will get from seq1 then chained seq2 so there we will get code as well as explaiantion
chain=seq1|seq2

#invoke the chain
res=chain.invoke({"question":"write a code in python for addition of two numbers simple code..."})


print(res['code'])
print(res['explaination'])