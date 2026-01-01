# assemble_agent.py
from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel
from schemas import NotionPagePayload

class CombinedContext(BaseModel):
    word_output: dict | None
    meaning_output: dict | None
    usage_output: dict | None

def build_assemble_agent(model='gemini-2.0-flash'):
    return Agent(
        model=model,
        name='assemble_agent',
        instruction="""
                    Input JSON:
                    { "word_output": {...} | null, "meaning_output": {...} | null, "usage_output": {...} | null }
                    Output ONLY a NotionPagePayload JSON.
                    Rules:
                    - domain: if missing/empty -> ["Daily Life"]
                    - related_words: join with ", " where needed; trim strings
                    - Trim all strings
                    No extra fields.
                    """,
        input_schema=CombinedContext,
        output_schema=NotionPagePayload,
        output_key='notion_payload'
    )