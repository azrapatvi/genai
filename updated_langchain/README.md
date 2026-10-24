# Updated LangChain (New Features)

Short notebooks that show the newer LangChain style.

| Notebook | What it shows |
|---|---|
| `agents.ipynb` | An agent is an LLM plus tools (example: a weather tool) |
| `pydantic_structured_output.ipynb` | Get a fixed-shape answer using Pydantic |
| `typedict_structured_output.ipynb` | Same idea using TypedDict (gives a plain dictionary) |
| `dataclass_structured_op.ipynb` | Same idea using a Python dataclass |
| `streaming_and_batch.ipynb` | Show the answer little by little, or answer many questions at once |
| `middleware.ipynb` | Auto-summarize a long chat so it stays short |
| `human_in_the_loop_middleware.ipynb` | Ask a human to approve, edit or reject before a tool runs |

## Setup
- Add `GROQ_API_KEY` to a `.env` file.
- Note: the first cell in `agents.ipynb` uses an OpenAI model. Use the Groq cell instead if you have no OpenAI key.
