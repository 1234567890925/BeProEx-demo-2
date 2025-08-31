from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
from ..config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder

def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedder()
    vectors = model.encode(texts, normalize_embeddings=True)
    return np.array(vectors, dtype=np.float32)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # expects normalized vectors
    return np.dot(a, b.T)

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    # Simple whitespace chunker
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunks.append(" ".join(chunk_words))
        if i + chunk_size >= len(words):
            break
        i += (chunk_size - overlap)
    return chunks
