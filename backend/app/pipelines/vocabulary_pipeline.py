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

def _parse_agent2(output: Any) -> NotionPagePayload:
    if isinstance(output, NotionPagePayload):
        return output
    obj = extract_json(str(output))
    return NotionPagePayload.model_validate(obj)

def run_clarify(term: str, context: str = "", prior: Optional[Dict[str, Any]] = None) -> Agent1Output:
    out = run_agent1(term=term, context=context, prior=prior)
    parsed = _parse_agent1(out)

    # Optional guardrail: force clarification if confidence below threshold
    if isinstance(parsed, ClarifiedInput) and parsed.confidence < settings.confidence_threshold:
        return ClarificationRequest(
            term=term,
            question=f"I’m not fully confident which sense of '{term}' you mean. Provide a short hint (e.g., business/music/sports).",
            choices=["business", "music", "sports", "finance", "other"],
        )
    return parsed

def run_generate_and_optionally_create(
    clarified: ClarifiedInput,
    create_page: bool = True
) -> Tuple[NotionPagePayload, Optional[Dict[str, Any]]]:
    out = run_agent2(clarified)
    payload = _parse_agent2(out)

    notion_result = None
    if create_page:
        notion = NotionClient(settings.notion_token, settings.notion_database_id)
        notion_result = notion.create_page(payload)

    return payload, notion_result
