from pydantic import BaseModel, Field
from typing import Optional

class WordOutput(BaseModel):
    word: str = Field(description="The target vocabulary word or phrase.")
    context: Optional[str] = Field(default=None, description="The user's intention or context for the word.")

class MeaningOutput(BaseModel):
    core_meaning: str = Field(description="The definition of the word.")
    meaning_type: str = Field(description="An explanation of the word's meaning.")
    domain: list[str] = Field(description="The domain or context in which the word is used.")

class UsageOutput(BaseModel):
    example: str = Field(description="An example sentence using the word.")
    usage_notes: Optional[str] = Field(default=None, description="Additional notes on how to use the word.")
    related_words: list[str] = Field(description="A list of words related to the target word.")

class NotionPagePayload(BaseModel):
    word: str = Field(description="The target vocabulary word or phrase.")
    core_meaning: str = Field(description="The definition of the word.")
    meaning_type: str = Field(description="An explanation of the word's meaning.")
    domain: list[str] = Field(description="The domain or context in which the word is used.")
    usage_notes: Optional[str] = Field(default=None, description="Additional notes on how to use the word.")
    example: str = Field(description="An example sentence using the word.")
    related_words: list[str] = Field(description="A list of words related to the target word.")

class MemoryOutput(BaseModel):
    status: str = Field(description="The status of the memory operation, e.g., 'saved' or 'failed'.")
    error: Optional[str] = Field(default=None, description="Error message if the operation failed.")