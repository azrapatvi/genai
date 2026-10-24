# MCP Demo

MCP (Model Context Protocol) puts tools on a separate server so any AI app can use them.

## Files
| File | What it does |
|---|---|
| `math_server.py` | Server with two tools: `add` and `multiply` |
| `weather_server.py` | Server with one tool: `weather` (always says "sunny" - demo only) |
| `client.py` | An AI agent that connects to both servers and uses their tools |

## Run it
1. Start the weather server in one terminal:
```
python weather_server.py
```
2. Start the client in another terminal:
```
python client.py
```
The client starts the math server by itself.

## Notes
- The weather server must be running at `http://localhost:8000/mcp`.
- Add `GROQ_API_KEY` to a `.env` file.
