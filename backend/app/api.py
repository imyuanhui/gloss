from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Any, Dict

from app.config import settings
from app.schemas.clarifier import ClarificationRequest, ClarifiedInput, Agent1Output
from app.schemas.generator import NotionPagePayload
from app.pipelines.vocabulary_pipeline import run_clarify, run_generate_and_optionally_create

router = APIRouter()

def require_auth(authorization: Optional[str] = Header(default=None)):
    if not settings.app_auth_token:
        return  # auth disabled
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.app_auth_token:
        raise HTTPException(status_code=403, detail="Invalid token")

class ClarifyRequest(BaseModel):
    term: str
    context: str = ""
    prior: Optional[Dict[str, Any]] = None  # may include user answer or previous state

class GenerateRequest(BaseModel):
    clarified_input: Dict[str, Any]
    create_notion_page: bool = True

@router.post("/clarify", response_model=Agent1Output, dependencies=[Depends(require_auth)])
def clarify(req: ClarifyRequest):
    return run_clarify(term=req.term, context=req.context, prior=req.prior)

@router.post("/generate", response_model=NotionPagePayload, dependencies=[Depends(require_auth)])
def generate(req: GenerateRequest):
    # Validate clarified_input shape
    clarified = ClarifiedInput.model_validate(req.clarified_input)
    payload, _page = run_generate_and_optionally_create(clarified, create_page=req.create_notion_page)
    return payload
