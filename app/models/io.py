from pydantic import BaseModel, Field
from typing import List

class SupportQuery(BaseModel):
    query: str = Field(..., description="Customer's free‑form question or issue")

class SupportResponse(BaseModel):
    final_answer: str
    sources: List[str]
