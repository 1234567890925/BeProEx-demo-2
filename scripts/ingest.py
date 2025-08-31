import os
from pathlib import Path
from typing import List, Dict, Any
from pymongo import MongoClient
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv

load_dotenv()

from app.config import MONGODB_URI, MONGO_DB, MONGO_COLLECTION
from app.agents.utils import chunk_text, embed_texts

KB_DIR = Path("data/kb")

def read_txt_files() -> List[Dict[str, Any]]:
    docs = []
    for p in KB_DIR.glob("*.txt"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        docs.append({"source": p.name, "text": txt})
    return docs

def main():
    docs = read_txt_files()
    if not docs:
        print(f"No .txt files found in {KB_DIR.resolve()}")
        return

    client = MongoClient(MONGODB_URI)
    coll = client[MONGO_DB][MONGO_COLLECTION]
    coll.drop()  # clean for fresh ingest
    print(f"Ingesting into {MONGO_DB}.{MONGO_COLLECTION} at {MONGODB_URI}")

    records = []
    for d in tqdm(docs, desc="Chunking"):
        chunks = chunk_text(d["text"])
        for i, ch in enumerate(chunks):
            records.append({"source": d["source"], "chunk_id": i, "text": ch})

    print(f"Embedding {len(records)} chunks...")
    embeddings = embed_texts([r["text"] for r in records])  # normalized

    for r, vec in zip(records, embeddings):
        r["embedding"] = vec.tolist()

    print("Writing to MongoDB...")
    if records:
        coll.insert_many(records, ordered=False)
    print("Done. Created", coll.count_documents({}), "chunks.")

if __name__ == "__main__":
    main()
