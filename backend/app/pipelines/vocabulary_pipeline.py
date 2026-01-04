from typing import Optional, Dict, Any, Tuple

from pydantic import ValidationError

from app.config import settings
from app.schemas.clarifier import Agent1Output, ClarificationRequest, ClarifiedInput
from app.schemas.generator import NotionPagePayload
from app.utils.json_extract import extract_json
from app.agents.agent1_clarifier import run_agent1
from app.agents.agent2_generator import run_agent2
from app.services.notion_client import NotionClient

def _parse_agent1(output: Any) -> Agent1Output:
    if isinstance(output, (ClarificationRequest, ClarifiedInput)):
        return output
    obj = extract_json(str(output))
    t = obj.get("type")
    if t == "clarification_request":
        return ClarificationRequest.model_validate(obj)
    if t == "clarified_input":
        return ClarifiedInput.model_validate(obj)
    raise ValueError("Agent1 output missing valid 'type' field")

def normalize_notion_payload_fields(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Agent2 output into a shape safe for NotionPagePayload validation.
    Fixes common LLM mistakes without altering meaning.
    """

    # usage_notes: must be string or None
    if "usage_notes" in obj:
        if isinstance(obj["usage_notes"], list):
            obj["usage_notes"] = " ".join(str(x) for x in obj["usage_notes"])
        elif obj["usage_notes"] is None:
            obj["usage_notes"] = ""

    # domain: must be list[str]
    if "domain" in obj:
        if isinstance(obj["domain"], str):
            obj["domain"] = [obj["domain"]]
        elif not isinstance(obj["domain"], list):
            obj["domain"] = []

    # related_words: must be list[str]
    if "related_words" in obj:
        if isinstance(obj["related_words"], str):
            obj["related_words"] = [
                w.strip() for w in obj["related_words"].split(",") if w.strip()
            ]
        elif not isinstance(obj["related_words"], list):
            obj["related_words"] = []

    return obj

def _parse_agent2(output: Any) -> NotionPagePayload:
    if isinstance(output, NotionPagePayload):
        return output
    obj = extract_json(str(output))
    obj = normalize_notion_payload_fields(obj)
    return NotionPagePayload.model_validate(obj)

def run_clarify(term: str, context: str = "") -> Agent1Output:
    out = run_agent1(term=term, context=context)
    parsed = _parse_agent1(out)
    return parsed

def run_generate_and_create(
    clarified: ClarifiedInput,
    create_page: bool = True
) -> Optional[Dict[str, Any]]:
    
    out = run_agent2(clarified)
    payload = _parse_agent2(out)
    notion_result = None
    if create_page:
        notion = NotionClient(settings.notion_token, settings.notion_data_source_id)
        notion_result = notion.create_page(payload)

    return notion_result
