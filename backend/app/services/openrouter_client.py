from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterClient:
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key

    # def chat(self, model: str, messages: List[Dict[str, Any]]) -> str:
    def chat(self, model: str, messages: List[Dict[str, Any]], max_tokens: int, temperature: float = 0.2) -> str:
        if settings.mock_mode:
            # In mock mode, the agents will bypass this anyway, but keep it safe.
            return "{}"

        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set and MOCK_MODE=false")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            # "max_tokens": max_tokens,
            # "temperature": temperature,
        }
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            r = client.post(OPENROUTER_URL, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
