from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Union, Dict, Any

from app.config import settings
from app.schemas.clarifier import ClarifiedInput, Agent1Output
from app.schemas.generator import NotionPagePayload
from app.pipelines.vocabulary_pipeline import run_clarify, run_generate_and_create

router = APIRouter()

def require_auth(authorization: Optional[str] = Header(default=None)):
    if not settings.app_auth_token:
        return  # auth disabled
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.app_auth_token:
        raise HTTPException(status_code=403, detail="Invalid token")

class LookupRequest(BaseModel):
    term: str
    context: Optional[str] = ""


LookupResponse = Union[Agent1Output, Dict[str, Any]]


@router.post("/lookup", response_model=LookupResponse, dependencies=[Depends(require_auth)])
def clarify(req: LookupRequest):
    output = run_clarify(term=req.term, context=req.context or "")
    if isinstance(output, ClarifiedInput):
        return run_generate_and_create(output, True)
    
    else:
        return output

# @router.post("/generate", response_model=NotionPagePayload, dependencies=[Depends(require_auth)])
# def generate(req: GenerateRequest):
#     # Validate clarified_input shape
#     clarified = ClarifiedInput.model_validate(req.clarified_input)
#     payload, _page = run_generate_and_create(clarified, create_page=req.create_notion_page)
#     return payload
