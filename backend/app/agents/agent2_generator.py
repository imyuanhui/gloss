from app.config import settings
from app.schemas.clarifier import ClarifiedInput
from app.schemas.generator import NotionPagePayload
from app.services.openrouter_client import OpenRouterClient

AGENT2_SYSTEM = """
                You are Agent 2: Vocabulary Generator.

                You receive a CLARIFIED input from Agent 1.
                The meaning is already decided. You MUST NOT reinterpret or change it.

                Return ONLY valid JSON matching EXACTLY the NotionPagePayload schema.
                No markdown. No commentary.

                ---

                Required output JSON:

                {
                "word": string,
                "core_meaning": string,
                "meaning_type": string,
                "domain": [string, ...],
                "usage_notes": string | null,
                "example": string,
                "related_words": [string, ...]
                }

                ---

                Rules (STRICT):

                word
                - Copy EXACTLY from the clarified input term.

                core_meaning
                - Copy the clarified meaning.
                - ONE concise sentence.
                - No hedging. No new senses.

                meaning_type
                - Copy EXACTLY from the clarified input.

                domain
                - Copy from clarified input.

                usage_notes
                - OPTIONAL.
                - MUST be a SINGLE STRING (never a list).
                - If multiple notes, merge into one string.
                - Use only for register, tone, regional or pragmatic notes.

                example
                - EXACTLY one natural sentence.
                - No quotes. No explanation.

                related_words
                - 3–6 single words.
                - Closely related.
                - No phrases. No duplicates.

                ---

                Hard constraints:
                - Do NOT output arrays for usage_notes.
                - Do NOT add fields.
                - Do NOT explain.
                - Do NOT contradict Agent 1.

                Input JSON contains:
                term, core_meaning, meaning_type, domain
                """

def run_agent2(clarified: ClarifiedInput) -> NotionPagePayload:
    # MOCK MODE: deterministic payload
    if settings.mock_mode:
        word = clarified.term
        sense = clarified.sense_hint
        domain = clarified.domain or (["general"] if sense == "general" else [sense])

        return NotionPagePayload(
            word=word,
            core_meaning=f"Mock definition of '{word}' (sense: {sense}).",
            meaning_type="Mock meaning_type describing the sense and usage pattern.",
            domain=domain,
            usage_notes="Mock usage notes (collocations, register, pitfalls).",
            example=f"Here is a mock example sentence using '{word}'.",
            related_words=["mock_related_1", "mock_related_2", "mock_related_3"],
        )

    # REAL MODE
    client = OpenRouterClient(settings.openrouter_api_key)
    models = settings.openrouter_models

    messages = [
        {"role": "system", "content": AGENT2_SYSTEM},
        {"role": "user", "content": clarified.model_dump_json()},
    ]

    last_err = None
    for model in models:
        try:
            content = client.chat(model=model, messages=messages, max_tokens=settings.llm_max_tokens_agent2, temperature=0.4)
            return content  # parsed/validated in pipeline
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Agent2 failed across models. Last error: {last_err}")
