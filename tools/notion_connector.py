import requests
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Union

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03"
}


def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


# def create_page(notionproperties: dict) -> dict:
#     url = "https://api.notion.com/v1/pages"

#     payload = {
#         "parent": {"data_source_id": DATA_SOURCE_ID},
#         "properties": notionproperties
#     }

#     response = requests.post(url, json=payload, headers=headers)
#     return {"status_code": response.status_code, "response": response.json()}

def _trim(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s2 = str(s).strip()
    return s2


def _normalize_domain(domain: Optional[List[str]]) -> List[str]:
    if not domain:
        return ["Daily Life"]
    out: List[str] = []
    for d in domain:
        td = _trim(d)
        if td:
            out.append(td)
    return out or ["Daily Life"]


def _normalize_related_words(words: Optional[List[str]]) -> List[str]:
    if not words:
        return []
    out: List[str] = []
    for w in words:
        tw = _trim(w)
        if tw:
            out.append(tw)
    return out


def build_notion_properties_from_payload(payload: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
    Build Notion 'properties' from a NotionPagePayload-shaped object.

    Accepts:
      - Pydantic model instance with attributes
      - dict with keys:
        word, core_meaning, meaning_type, domain, usage_notes, example, related_words

    Applies rules:
      - trim all strings
      - domain default -> ["Daily Life"] if empty
      - related_words joined with ", " for "Related Words" rich_text; if empty -> []
    """
    # Support either dict-like or attribute-like inputs
    def get(key: str, default=None):
        if isinstance(payload, dict):
            return payload.get(key, default)
        return getattr(payload, key, default)

    word = _trim(get("word")) or ""
    core_meaning = _trim(get("core_meaning")) or ""
    meaning_type = _trim(get("meaning_type")) or ""
    domain = _normalize_domain(get("domain"))
    usage_notes = _trim(get("usage_notes"))
    example = _trim(get("example")) or ""
    related_words = _normalize_related_words(get("related_words"))

    related_joined = ", ".join(related_words)

    properties: Dict[str, Any] = {
        "Word / Phrase": {
            "title": [{"text": {"content": word}}]
        },
        "Core Meaning": {
            "rich_text": [{"text": {"content": core_meaning}}]
        },
        "Meaning Type": {
            "select": {"name": meaning_type}
        },
        "Domain": {
            "multi_select": [{"name": d} for d in domain]
        },
        "Usage Notes": {
            "rich_text": [{"text": {"content": usage_notes}}] if usage_notes else []
        },
        "Example": {
            "rich_text": [{"text": {"content": example}}]
        },
        "Related Words": {
            "rich_text": [{"text": {"content": related_joined}}] if related_joined else []
        },
    }
    return properties


def create_page(notionproperties_or_payload: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
    Create a Notion page.

    Backward compatible:
      - If passed a dict that ALREADY looks like Notion 'properties' (has 'Word / Phrase', etc),
        it will use it directly.
      - If passed a NotionPagePayload (or dict with its fields), it will build properties first.
    """
    if NOTION_TOKEN is None or DATA_SOURCE_ID is None:
        return {
            "status_code": 500,
            "response": {"error": "Missing NOTION_TOKEN or DATA_SOURCE_ID in environment."},
        }

    # Heuristic: if the dict already contains Notion property keys, treat as properties.
    if isinstance(notionproperties_or_payload, dict) and "Word / Phrase" in notionproperties_or_payload:
        notion_properties = notionproperties_or_payload
    else:
        notion_properties = build_notion_properties_from_payload(notionproperties_or_payload)

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"data_source_id": DATA_SOURCE_ID},
        "properties": notion_properties,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return {"status_code": response.status_code, "response": response.json()}
    except requests.RequestException as e:
        return {"status_code": 500, "response": {"error": str(e)}}