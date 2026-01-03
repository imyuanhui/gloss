from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

def _csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

class Settings(BaseModel):
    mock_mode: bool = os.getenv("MOCK_MODE", "true").lower() == "true"

    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    openrouter_models: List[str] = _csv(os.getenv(
        "OPENROUTER_MODELS",
        "qwen/qwen3-4b:free,deepseek/deepseek-r1-0528:free,xiaomi/mimo-v2-flash:free"
    ))

    notion_token: Optional[str] = os.getenv("NOTION_TOKEN")
    notion_data_source_id: Optional[str] = os.getenv("NOTION_DATA_SOURCE_ID")

    app_auth_token: Optional[str] = os.getenv("APP_AUTH_TOKEN") or None
    cors_origins: List[str] = _csv(os.getenv("CORS_ORIGINS", "http://127.0.0.1:3000"))

    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    llm_max_tokens_agent1: int = int(os.getenv("LLM_MAX_TOKENS_AGENT1", "300"))
    llm_max_tokens_agent2: int = int(os.getenv("LLM_MAX_TOKENS_AGENT2", "700"))

settings = Settings()