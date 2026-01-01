from google.adk.agents.llm_agent import Agent
from tools.notion_connector import create_page
from schemas import MemoryOutput, NotionPagePayload

def build_memory_agent(memory_agent_model = 'gemini-2.0-flash') -> Agent:
    memory_agent = None
    try:
        memory_agent = Agent(
            model = memory_agent_model,
            name="memory_agent",
            instruction="""
                        You are Gloss Memory Agent. Persist a vocabulary entry to Notion via create_page.
                        Input (NotionPagePayload):
                        { "word","core_meaning","meaning_type","domain","usage_notes","example","related_words" }
                        Call create_page(NotionPagePayload).
                        Return ONLY:
                        { "status":"saved" } OR { "status":"failed","error":"<reason>" }.
                        """,
            description="Create a notion page using the 'create_page' tool.",
            input_schema=NotionPagePayload,
            output_schema= MemoryOutput,
            output_key="memory_output",
            tools=[create_page],
        )
        print(f"✅ Agent '{memory_agent.name}' created using model '{memory_agent.model}'.")
    except Exception as e:
        print(f"❌ Could not create Memory agent. Check API Key ({memory_agent_model}). Error: {e}")

    return memory_agent

