from typing import Optional, Dict, Any
import httpx

from app.config import settings
from app.schemas.generator import NotionPagePayload

NOTION_VERSION = "2025-09-03"

class NotionClient:
    def __init__(self, token: Optional[str], data_source_id: Optional[str]):
        self.token = token
        self.data_source_id = data_source_id

    def create_page(self, payload: NotionPagePayload) -> Dict[str, Any]:
        if settings.mock_mode:
            return {"id": "mock-page-id", "url": "https://www.notion.so/mock-page"}

        if not self.token or not self.data_source_id:
            raise RuntimeError("NOTION_TOKEN/NOTION_data_source_ID not set and MOCK_MODE=false")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

        url = "https://api.notion.com/v1/pages"

        # Property mapping
        properties = {
            "Word / Phrase": {"title": [{"text": {"content": payload.word}}]},
            "Core Meaning": {"rich_text": [{"text": {"content": payload.core_meaning}}]},
            "Meaning Type": {"rich_text": [{"text": {"content": payload.meaning_type}}]},
            "Domain": {"multi_select": [{"name": d} for d in payload.domain]},
            "Usage Notes": {"rich_text": [{"text": {"content": payload.usage_notes or ""}}]},
            "Example": {"rich_text": [{"text": {"content": payload.example}}]},
            "Related Words": {"multi_select": [{"name": w} for w in payload.related_words]},
        }

        body = {
            "parent": {"data_source_id": self.data_source_id},
            "properties": properties,
        }

        with httpx.Client(timeout=30) as client:
            r = client.post(url, headers=headers, json=body)
            r.raise_for_status()
            return r.json()
