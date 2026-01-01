from google.adk.agents.llm_agent import Agent
from schemas import WordOutput

def build_word_agent(word_agent_model = 'gemini-2.0-flash') -> Agent:
    word_agent = None
    try:
        word_agent = Agent(
            model = word_agent_model,
            name="word_agent",
            instruction="""
                        You are Gloss Word Agent.
                        Input: user text about a vocabulary word/phrase.
                        Goal: extract target word/phrase and a brief context (user intent).
                        If ambiguity is HIGH (multiple common meanings and no context):
                        - Do NOT define or guess.
                        - Return a compact picker with 2–4 options.
                        - Proceed only after user selects.
                        If ambiguity is LOW or resolved:
                        Return ONLY JSON with exactly:
                        { "word": string, "context": string }
                        No extra text.
                        """,
            description="An agent that extracts the target vocabulary word or phrase along with context from user input. Interacts to resolve ambiguities if needed.",
            output_schema= WordOutput,
            output_key="word_output",
        )
        print(f"✅ Agent '{word_agent.name}' created using model '{word_agent.model}'.")
    except Exception as e:
        print(f"❌ Could not create Word agent. Check API Key ({word_agent_model}). Error: {e}")

    return word_agent


