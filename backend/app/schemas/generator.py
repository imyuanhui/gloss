from typing import List, Optional
from pydantic import BaseModel, Field

class NotionPagePayload(BaseModel):
    word: str = Field(description="The target vocabulary word or phrase.")
    core_meaning: str = Field(description="The definition of the word.")
    meaning_type: str = Field(description="An explanation of the word's meaning.")
    domain: List[str] = Field(description="The domain or context in which the word is used.")
    usage_notes: Optional[str] = Field(default=None, description="Additional notes on how to use the word.")
    example: str = Field(description="An example sentence using the word.")
    related_words: List[str] = Field(description="A list of words related to the target word.")
