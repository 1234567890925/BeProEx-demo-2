#from .llm import LLMClient
from app.agents.llm import LLMClient



COMM_SYSTEM = """    You are a friendly, empathetic customer support writer.
Transform the technical draft into a clear, reassuring message with actionable steps.
Rules:
- Start with a brief empathy line (1 short sentence).
- Present steps as a concise ordered list the customer can follow.
- Keep strictly grounded in the provided sources; do NOT invent.
- If the draft requests clarifying info, include a brief question at the end.
- Include a short 'Why this works' note if helpful.
- Avoid jargon unless necessary; explain terms plainly.
Output only the final message.
"""

def refine_for_customer(original_query: str, draft_solution: str, sources_joined: str, llm: LLMClient) -> str:
    user = (
        f"Customer query: {original_query}\n\n"
        f"Technical draft:\n{draft_solution}\n\n"
        f"(For grounding) Sources:\n{sources_joined}\n\n"
        "Write the final customer-friendly answer now."
    )
    return llm.chat(system=COMM_SYSTEM, user=user)
