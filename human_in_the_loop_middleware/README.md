# Human in the Loop

The AI stops and asks a human before doing something important.

## Files
| File | What it does |
|---|---|
| `hitl_llm.ipynb` | Every question needs your yes/no before the AI answers |
| `chatbot_to_purhase_stock.py` | A stock chatbot in the terminal. It shows live prices and asks yes/no before "buying" |

## Run it
```
python chatbot_to_purhase_stock.py
```

## Notes
- The stock purchase is only a **simulation**. No real money is used.
- Live prices come from Alpha Vantage, so you need its API key in a `.env` file.
- Add `GROQ_API_KEY` too.
