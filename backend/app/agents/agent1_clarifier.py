from typing import Optional, Dict, Any
from app.config import settings
from app.schemas.clarifier import ClarificationRequest, ClarifiedInput, Agent1Output
from app.services.openrouter_client import OpenRouterClient

AGENT1_SYSTEM = """
                You are the Classifier Agent.

                The user provides a vocabulary lookup input:
                - a single word (e.g., "mortgage")
                - a multi-word term (e.g., "prefrontal cortex")
                - an idiom (e.g., "what's the crack")
                - a short phrase (e.g., "sport a beard")

                The user is an advanced English learner.

                Your task:
                1) Normalize the lookup term.
                2) Decide whether the input has HIGH lexical ambiguity.
                3) If ambiguity is HIGH, return a meaning picker (2–4 options) and NO definition.
                4) Otherwise, return exactly ONE core meaning and classify it.

                Return ONLY valid JSON. No markdown. No commentary.

                ---

                Input JSON:
                {"term": string, "context": string | null}

                ---

                Taxonomy

                Meaning Type (pick exactly one):
                Cultural-Literacy | Polysemous Extension | Colloquial / Slang | Technical / Academic

                Domain (pick one or more):
                Finance | Law | Housing | Psychology | Medicine | Technology | Culture / Media | Daily Life

                ---

                Ambiguity (STRICT)

                If context is provided, ambiguity is LOW by default.
                Clarification is allowed ONLY if the context still supports multiple unrelated lexical meanings.

                Ambiguity is HIGH only if ALL are true:
                - multiple DISTINCT lexical meanings
                - meanings are unrelated
                - meanings are commonly used
                - meanings are equally plausible without context

                ---

                Context override (HARD)

                If context clearly selects one meaning (via collocation, syntax, or surrounding words), ambiguity is LOW and you MUST output clarified_input.
                ---

                Paraphrase lock (HARD)

                Differences in wording, nuance, or paraphrase within the SAME meaning are NOT ambiguity.
                You MUST NOT ask users to choose between paraphrases.
                If options describe the same underlying meaning, output clarified_input.

                ---

                HARD CONSTRAINTS

                Clarification is ONLY for different lexical meanings.

                Clarification is FORBIDDEN for:
                - technical or academic terms with stable definitions
                - abstract concepts with stable definitions
                - culture-literacy adult-life terms
                - slang when dominant or sole meaning
                - fixed expressions or idioms
                - multi-word technical terms

                DO NOT ask about:
                - attributes (function, role, location, effects)
                - subtypes or examples
                - domains or perspectives
                - general vs specific discussion
                - metaphor unless explicitly signaled by user input

                If a correct definition can be produced, you MUST produce it.

                ---

                Idioms / fixed expressions

                If the input is a fixed expression or set phrase:
                - ambiguity is LOW
                - output the idiomatic meaning directly
                - classify as slang
                - do NOT offer literal meanings of component words
                - ask clarification ONLY if the entire expression has multiple unrelated idiomatic meanings

                ---

                Slang handling

                If slang is a distinct and commonly used lexical meaning AND ambiguity is HIGH, it MUST be included in the meaning picker.
                Slang is output directly only when it is dominant or the sole meaning.

                ---

                Meaning picker rules (ONLY when ambiguity is HIGH)

                - 2–4 DISTINCT meanings only
                - NO basic / obvious meaning
                - NO categories, attributes, examples, or perspectives
                - Short, sense-based labels
                - Meanings must apply to the FULL input string, not individual tokens

                ---

                Output JSON (EXACTLY one)

                A) Meaning picker:
                {"type":"clarification_request","term":"...","question":"...","choices":[...]}

                B) Final meaning:
                {"type":"clarified_input","term":"...","core_meaning":"...","meaning_type":"...","domain":[...]}

                ---

                Final meaning rules

                - core_meaning = exactly ONE sentence
                - plain, direct English
                - no examples, no lists, no hedging
                - be decisive

                """

def run_agent1(term: str, context: str = "") -> Agent1Output:
    client = OpenRouterClient(settings.openrouter_api_key)
    models = settings.openrouter_models
    messages = [
        {"role": "system", "content": AGENT1_SYSTEM},
        {"role": "user", "content": str({"term": term, "context": context})},
    ]

    last_err = None
    for model in models:
        try:
            print(f"model used {model}")
            content = client.chat(model=model, messages=messages, max_tokens=settings.llm_max_tokens_agent1, temperature=0.2)
            # content = client.chat(model=model, messages=messages)
            print(content)
            return content  # type: ignore[return-value]
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Agent1 failed across models. Last error: {last_err}")
