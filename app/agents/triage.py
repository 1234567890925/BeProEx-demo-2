#from .llm import LLMClient
from app.agents.llm import LLMClient



TRIAGE_SYSTEM = """    You are a Tier‑1 technical support triage specialist.
- Rewrite vague customer questions into a precise, technical search query.
- Keep it concise (max 1 sentence).
- Include product keywords and likely subsystem names (Bluetooth, Wi‑Fi, battery, pairing, factory reset, etc.).
- Do NOT answer the question yet; just output the refined query.
"""

def triage_rewrite(raw_query: str, llm: LLMClient) -> str:
    user = f"Customer query: {raw_query}\nRewrite as a single precise technical query for searching a knowledge base."
    return llm.chat(system=TRIAGE_SYSTEM, user=user)
