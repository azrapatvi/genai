# Basic Chatbot (LangGraph Lessons)

A notebook diary. Each file teaches one new idea about LangGraph.

| File | What you learn |
|---|---|
| `basic_chatbot.ipynb` | Your first chatbot: state, nodes, edges and tools |
| `chatbot_withmemory_langraph.ipynb` | Make the bot remember things using a `thread_id` |
| `chatbot_for_joke.ipynb` | Custom state and going back to an earlier step |
| `chat_humanintheloop.ipynb` | Pause the bot and wait for a human answer |
| `email_humanintheloop.ipynb` | Ask "send this email? yes/no" first (practice only) |
| `debugging.ipynb` | See every step using LangSmith tracing |
| `fault_tolerance.ipynb` | Empty notebook (saved for later) |
| `parallel_runnables.ipynb` | Run two chains at the same time |
| `runnable_passthorugh.py` | Pass an answer from one chain to the next |
| `screen_reader.ipynb` | First test: send a screenshot to a vision model |
| `simple_multiaiagent.ipynb` | Two agents: a researcher and a writer |
| `superviser_multiai_agent.ipynb` | A supervisor who manages many agents |
| `sample.png` | A sample screenshot used in a test |

## Setup
- Add `GROQ_API_KEY` to a `.env` file.
- Some notebooks also need `TAVILY_API_KEY` (web search) or `LANGCHAIN_API_KEY` (tracing).
