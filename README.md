## BeProEx AI Support —

Take-Home Assessment: AI Customer Support Agent.

This repository contains a small but complete AI support backend that I wrote to be transparent and easy to reason about. It accepts a single question from a user, decides whether the question is technical or not, looks up relevant information from a local knowledge base, asks a language model to draft a solution, and then rewrites that solution so a customer can understand it without any jargon. I am intentionally not using LangChain here so that every step is visible in normal Python, and you can see exactly what is happening.

## What actually happens when you send a request

When you send a POST request to /support-query with a JSON body that contains a single field named "query", FastAPI receives the request and validates the payload against a Pydantic model. If the payload is valid, the application passes the query string into a small routing function. That routing function asks the language model a very constrained question: it only needs to say whether this query should be handled as a technical issue or as a general communication. I keep this step minimal on purpose because it keeps the downstream behavior predictable.

If the router says that the query is technical, the code collects context before drafting any response. It looks inside the data/kb directory, reads the text files, and prepares short snippets that are related to the user’s question. If you enable the optional MongoDB mode, the code instead queries a vector index in MongoDB or Atlas; this returns the top K snippets already sorted by similarity to the query. The program does not show raw embeddings to you; it only uses them to choose which sentences are most likely to help. The selected snippets are then fed to the language model with clear instructions to propose a step-by-step solution that a support engineer would be comfortable sending to a colleague.

Regardless of whether the query was technical or not, the program then runs a final rewrite pass. This pass asks the model to take the existing draft and turn it into a short, polite message that a customer will find clear and actionable. The rewrite step deliberately avoids internal jargon and preserves the actual steps. Finally, the FastAPI endpoint returns a JSON response that contains the final_answer along with a list of sources so you can see what material informed the draft.

---

## Project layout

I built this in a sequence of small, understandable steps. Routing is separated from solution drafting so that the model only has to make one decision at a time. Retrieval is separated from drafting so that you can swap in a different retrieval method without altering the prompt. The final rewrite is separated from drafting so that we do not mix customer tone with technical correctness. These boundaries make testing simpler and they make failures easier to diagnose.
---

## Tech used

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- OpenAI Python SDK
- Database: MongoDB or Atlas Vector Search (via scripts/ingest.py)
- Testing: Postman or curl for testing

---

## Setup

1) Create .env (do not commit it)
```
OPENAI_API_KEY=sk-***
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.2

# Mongo/Atlas (only if you want vector search)
MONGODB_URI=mongodb://localhost:27017
MONGO_DB=beproex
MONGO_COLLECTION=kb
USE_ATLAS_VECTOR_SEARCH=false
TOP_K=4
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Optional: start Mongo locally
```bash
docker compose up -d
```

4) Optional: ingest KB into Mongo (only if USE_ATLAS_VECTOR_SEARCH=true)
Run from project root so Python can import app.*
```bash
python -m scripts.ingest
```

---

## Run the server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

---

## Testing



Postman
- Method: POST
- URL: http://127.0.0.1:8000/support-query
- Body: raw JSON
```json
{
  "query": "My new drone will not connect to the app"
}
```

curl
```bash
curl -X POST "http://127.0.0.1:8000/support-query"   -H "Content-Type: application/json"   -d '{"query":"Drone WiFi connect nahi ho raha"}'
```

Expected response (shape):
```json
{
  "final_answer": "polite, actionable steps",
  "sources": ["snippet or filename ref"]
}
```

---

## How it works

1) Triage (app/agents/triage.py)  
   A short system prompt asks the model to label the query (TECH or COMM).

2) Technical draft (app/agents/technical.py)  
   - If USE_ATLAS_VECTOR_SEARCH=false, embed or keyword-score local KB files, compute cosine similarity, pick top-K snippets.
   - If USE_ATLAS_VECTOR_SEARCH=true, query Mongo/Atlas vector index (after scripts/ingest.py) for top-K results.
   - Prompt the model to produce a clear, step-by-step solution grounded in those snippets.

3) Customer rewrite (app/agents/communication.py)  
   Turn the draft into a clear, courteous, and concise customer reply. Preserve sources for transparency.

4) LLM client (app/agents/llm.py)  
    small wrapper around the OpenAI SDK:
   ```python
   resp = client.chat.completions.create(
       model=self.model, temperature=self.temperature,
       messages=[{"role": "system", "content": system},
                 {"role": "user", "content": user}]
   )
   ```

---

## Challenges Faced

- Ensuring all runs are from project root — relative imports break otherwise.
- Dealing with stdlib name collisions (e.g., `io`, `json`) when structuring modules.
- Keeping imports consistent — mixing relative and package-style imports caused confusion.
- Running scripts reliably: some required `python -m` invocation to resolve dependencies.
- Handling ingestion quirks — ensuring paths and data formats stayed consistent across runs.

---

## Quick checklist

- .env has a valid OPENAI_API_KEY
- Optional: Mongo up, USE_ATLAS_VECTOR_SEARCH=true, and python -m scripts.ingest
- Run: python -m uvicorn app.main:app --reload --port 8000
- Test: POST /support-query in Postman or curl

Good to go.
