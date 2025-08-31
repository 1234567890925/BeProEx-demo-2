from typing import Dict, Any, List, Tuple
from pymongo import MongoClient
import numpy as np
#from .llm import LLMClient
#from .utils import embed_texts, cosine_sim
#from ..config import MONGODB_URI, MONGO_DB, MONGO_COLLECTION, USE_ATLAS_VECTOR_SEARCH, TOP_K

from app.agents.llm import LLMClient

from app.agents.utils import embed_texts, cosine_sim
from app.config import MONGODB_URI, MONGO_DB, MONGO_COLLECTION, USE_ATLAS_VECTOR_SEARCH, TOP_K


TECHNICAL_SYSTEM = """    You are a meticulous technical expert. Using the provided knowledge chunks, draft a DIRECT, step‑by‑step solution.
Rules:
- Cite ONLY from the given chunks.
- If info is insufficient, say what is missing and request the minimum clarifying detail.
- Use enumerated steps and keep it factual (no fluff).
Output only the draft solution, no extra commentary.
"""

def _retrieve_from_atlas(query_vec: np.ndarray, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    client = MongoClient(MONGODB_URI)
    coll = client[MONGO_DB][MONGO_COLLECTION]
    pipeline = [
        {
            "$vectorSearch": {
                "index": "default",  # ensure your vector index name
                "path": "embedding",
                "numCandidates": max(50, top_k*5),
                "queryVector": query_vec.flatten().tolist(),
                "limit": top_k
            }
        },
        {"$project": {"text": 1, "source": 1, "chunk_id": 1, "_id": 0}},
    ]
    return list(coll.aggregate(pipeline))

def _retrieve_fallback(query_vec: np.ndarray, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    client = MongoClient(MONGODB_URI)
    coll = client[MONGO_DB][MONGO_COLLECTION]
    docs = list(coll.find({}, {"_id": 0, "text": 1, "source": 1, "chunk_id": 1, "embedding": 1}))
    if not docs:
        return []
    mat = np.array([d["embedding"] for d in docs], dtype=np.float32)
    sims = (mat @ query_vec.T).flatten()  # embeddings already normalized in ingest
    top_idx = np.argsort(-sims)[:top_k]
    results = [ {k:v for k,v in docs[i].items() if k != "embedding"} for i in top_idx ]
    return results

def retrieve_chunks(technical_query: str) -> List[Dict[str, Any]]:
    qvec = embed_texts([technical_query])  # normalized
    if USE_ATLAS_VECTOR_SEARCH:
        try:
            return _retrieve_from_atlas(qvec)
        except Exception:
            # fall back if vector index is not ready
            return _retrieve_fallback(qvec)
    else:
        return _retrieve_fallback(qvec)

def draft_solution(technical_query: str, llm: LLMClient) -> Tuple[str, List[str]]:
    chunks = retrieve_chunks(technical_query)
    sources_for_llm = "\n---\n".join([f"[{c['source']}#{c['chunk_id']}]\n{c['text']}" for c in chunks])
    user = f"Technical query: {technical_query}\n\nKnowledge chunks:\n{sources_for_llm}\n\nWrite the DRAFT solution now."
    draft = llm.chat(system=TECHNICAL_SYSTEM, user=user)
    human_sources = [f"{c['text']} [{c['source']}#{c['chunk_id']}]" for c in chunks]
    return draft, human_sources
