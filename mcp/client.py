#this file needs to be interact with math server and weather server
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent # we need to create an agent who is resposnible for interacting with these tooosl
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import asyncio

import sys
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

async def main():

    client = MultiServerMCPClient({
        "math_server": {
            "command": sys.executable,
            "args": [str(BASE_DIR / "math_server.py")],
            "transport": "stdio"
        },
        "weather_server": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http"
        }
    })

    tools = await client.get_tools() # to get both defined tools

    print("Available tools:", [tool.name for tool in tools])

    model = ChatGroq(model="openai/gpt-oss-120b")

    agent = create_react_agent(model, tools)

    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "What is 2 + 2?"}
        ]
    })

    print(response["messages"][-1].content)

    response = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "todays weather in ratnagiri"}
            ]
        })
    
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())