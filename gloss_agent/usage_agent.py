from google.adk.agents.llm_agent import Agent
from schemas import MeaningOutput, UsageOutput

def build_usage_agent(usage_agent_model = 'gemini-2.0-flash') -> Agent:
    usage_agent = None
    try:
        usage_agent = Agent(
            model = usage_agent_model,
            name="usage_agent",
            instruction="""
                        You are Usage Agent.
                        Input JSON (meaning_output):
                        { "core_meaning": string, "meaning_type": string, "domain": string[] }
                        Output ONLY JSON with exactly:
                        {
                        "usage_notes": string,
                        "example": string,
                        "related_words": string[]
                        }
                        Constraints:
                        - usage_notes: 1–2 sentences, no bullets.
                        - example: single sentence, no quotes, no parentheses.
                        - related_words: 2–4 plain strings.
                        No extra fields. Do not redefine or reclassify.
                        """,
            description="An agent that explains how a word or phrase is used by native speakers.",
            input_schema=MeaningOutput,
            output_schema=UsageOutput,
            output_key="usage_output",
        )
        print(f"✅ Agent '{usage_agent.name}' created using model '{usage_agent.model}'.")
    except Exception as e:
        print(f"❌ Could not create Usage agent. Check API Key ({usage_agent_model}). Error: {e}")

    return usage_agent