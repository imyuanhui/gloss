from google.adk.agents.llm_agent import Agent
from schemas import WordOutput, MeaningOutput

def build_meaning_agent(meaning_agent_model = 'gemini-2.0-flash') -> Agent:
    meaning_agent = None
    try:
        meaning_agent = Agent(
            model = meaning_agent_model,
            name="meaning_agent",
            instruction="""
                        You are Gloss Meaning Agent.
                        Input JSON (from word_agent):
                        { "word": string, "context": string }
                        Output ONLY JSON with exactly:
                        { "core_meaning": string, "meaning_type": string, "domain": string[] }
                        Rules:
                        - Provide ONE core meaning matching the user intent.
                        - Choose exactly ONE meaning_type from:
                        ["Core Lexical","Cultural-Literacy","Polysemous Extension","Colloquial / Slang","Technical / Academic"]
                        - domain: one or more from:
                        ["Finance","Law","Housing","Psychology","Medicine","Technology","Culture / Media","Daily Life"]
                        - No examples. No usage notes. No questions. No extra fields.
                        """,
            description="An agent that determines the core meaning of a word or phrase and classifies it using the Gloss taxonomy.",
            input_schema=WordOutput,
            output_schema= MeaningOutput,
            output_key="meaning_output",
        )
        print(f"✅ Agent '{meaning_agent.name}' created using model '{meaning_agent.model}'.")
    except Exception as e:
        print(f"❌ Could not create Meaning agent. Check API Key ({meaning_agent_model}). Error: {e}")

    return meaning_agent