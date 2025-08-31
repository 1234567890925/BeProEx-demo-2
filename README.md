# BeProEx – AI Customer Support Agent (Multi‑Agent RAG)

A three‑agent FastAPI system that ingests product manuals/FAQs, retrieves relevant chunks from MongoDB, and crafts friendly, grounded support replies.

## Architecture (Triage → Technical → Communication)

1) **Triage Specialist**: rewrites vague user text into a precise, searchable technical query.  
2) **Technical Expert**: RAG core – retrieves top‑K chunks from MongoDB using vector search (Atlas or fallback cosine) and drafts a factual solution.  
3) **Communication Specialist**: turns the draft into an empathetic, step‑by‑step customer answer with zero fabrication beyond sources.

---

## Quick Start

### 0) Clone & set up env
```bash
cp .env.example .env
# edit .env with your keys / settings
```

### 1) Start MongoDB (local)
```bash
docker compose up -d
```

### 2) Install deps & run ingestion
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# put your .txt manuals/FAQs in data/kb/
python scripts/ingest.py
```

### 3) Run the API
```bash
uvicorn app.main:app --reload --port ${PORT:-8000}
```

### 4) Test the endpoint
```bash
curl -s -X POST "http://localhost:8000/support-query"       -H "Content-Type: application/json"       -d '{"query": "My new drone will not connect to the app"}' | jq .
```

---

## MongoDB Vector Search (Atlas) – optional but recommended
If you host your collection on Atlas, set `USE_ATLAS_VECTOR_SEARCH=true` in `.env`, then create a vector search index (replace db/collection names if needed):

```jsonc
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,     // all-MiniLM-L6-v2
      "similarity": "cosine"
    },
    { "type": "string", "path": "source" }
  ]
}
```

The app will auto‑detect this setting and use `$vectorSearch`. If `false`, it falls back to fetching embeddings and computing cosine similarities in Python (fine for small KBs).

---

## Files & Folders

```
app/
  main.py
  config.py
  agents/
    __init__.py
    llm.py
    triage.py
    technical.py
    communication.py
    utils.py
  models/
    __init__.py
    io.py
scripts/
  ingest.py
data/kb/
  drone_getting_started.txt
  drone_connectivity_faq.txt
docker-compose.yml
requirements.txt
.env.example
README.md
```

---

## Notes
- Embeddings use **sentence-transformers/all‑MiniLM‑L6‑v2** (open‑source).
- LLM defaults to **OpenAI** (`LLM_MODEL=gpt-4o-mini`) – change in `.env`.
- Grounding: the Communication agent is instructed not to invent facts beyond the retrieved sources. If coverage is insufficient, it will ask for clarifying info.

---

## Example Response
```json
{
  "final_answer": "Sorry you're hitting pairing issues. Let's fix it...",
  "sources": [
    "Section: App Pairing Basics — Ensure Bluetooth is on... [drone_getting_started.txt#0]",
    "Troubleshooting Wi‑Fi/Bluetooth conflicts... [drone_connectivity_faq.txt#1]"
  ]
}
```

---

## Local Dev Tips
- Regenerate embeddings anytime you update files in `data/kb/` by re‑running `scripts/ingest.py`.
- You may seed more domain docs; everything is plain `.txt`.
- For production, consider: auth for the API, request logging, rate limits, vector DB indexes, and async batching for retrieval.
# BeProEx-demo-2
# BeProEx-demo-2
# BeProEx-demo-2
