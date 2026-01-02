from typing import List, Union, Literal
from pydantic import BaseModel, Field

from .enums import MeaningType


class ClarificationRequest(BaseModel):
    type: Literal["clarification_request"] = "clarification_request" # Identifies this output as a clarification request
    term: str # The word or phrase the user originally entered
    question: str # A single, focused question to resolve ambiguity
    choices: List[str] = Field(default_factory=list) # Predefined options to guide the user’s response


class ClarifiedInput(BaseModel):
    type: Literal["clarified_input"] = "clarified_input" # Identifies this output as a clarified interpretation
    term: str # The word or phrase the user originally entered
    core_meaning: str # The resolved core definition for the intended meaning
    meaning_type: MeaningType # The category describing the nature of this meaning
    domain: List[str] = Field(default_factory=list) # One or more subject domains where this meaning is commonly used


Agent1Output = Union[ClarificationRequest, ClarifiedInput]