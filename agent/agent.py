from google.adk.agents.llm_agent import Agent
from tools.notion_connector import create_page

# Try relative import when package is present; if running as a script (no parent package),
# fall back to local import from the prompts package.
try:
    from .prompts.build_prompt import (
        build_root_agent_prompt,
        build_meaning_agent_prompt,
        build_usage_agent_prompt,
        build_memory_agent_prompt,
    )
except Exception:
    from prompts.build_prompt import (
        build_root_agent_prompt,
        build_meaning_agent_prompt,
        build_usage_agent_prompt,
        build_memory_agent_prompt,
    )

ROOT_PROMPT = build_root_agent_prompt()
MEANING_PROMPT = build_meaning_agent_prompt()
USAGE_PROMPT = build_usage_agent_prompt()
MEMORY_PROMPT = build_memory_agent_prompt()


# Allow running this module directly for a quick smoke test.
if __name__ == "__main__":
    # Print short slices of each prompt to verify imports work in different contexts.
    print("ROOT_PROMPT:", ROOT_PROMPT[:200])
    print("MEANING_PROMPT:", MEANING_PROMPT[:200])
    print("USAGE_PROMPT:", USAGE_PROMPT[:200])
    print("MEMORY_PROMPT:", MEMORY_PROMPT[:200])

meaning_agent = Agent(
    model='gemini-2.5-flash',
    name='meaning_agent',
    description='Meaning Agent: Responsible for understanding and generating definitions, explanations, and contextual meanings of vocabulary words.',
    instruction=MEANING_PROMPT
)

usage_agent = Agent(
    model='gemini-2.5-flash',
    name='usage_agent',
    description='Usage Agent: Responsible for generating example sentences and usage contexts for vocabulary words.',
    instruction=USAGE_PROMPT
)

memory_agent = Agent(
    model='gemini-2.5-flash',
    name='memory_agent',
    description='Memory Agent: Responsible for creating page for a term in Notion.',
    instruction=MEMORY_PROMPT,
    tools=[create_page]
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Gloss Root Agent: Orchestrates other agents to process user requests related to vocabulary learning and management.',
    instruction=ROOT_PROMPT,
    sub_agents=[meaning_agent, usage_agent, memory_agent]
)