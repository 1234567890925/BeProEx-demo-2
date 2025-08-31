import os
from typing import Optional
from openai import OpenAI
#from ..config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, temperature: float = LLM_TEMPERATURE):
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is missing. Please set it in .env")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model or LLM_MODEL
        self.temperature = temperature

    def chat(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content.strip()
