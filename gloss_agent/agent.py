from google.adk.agents.llm_agent import Agent
from dotenv import load_dotenv
from word_agent import build_word_agent
from meaning_agent import build_meaning_agent
from usage_agent import build_usage_agent
from assembly_agent import build_assemble_agent
from memory_agent import build_memory_agent

from google.adk.models.lite_llm import LiteLlm

load_dotenv()  # Load environment variables from .env file

model=LiteLlm(model="openai/gpt-4.1-mini")

word_agent = build_word_agent(model)
meaning_agent = build_meaning_agent(model)
usage_agent = build_usage_agent(model)
assemble_agent = build_assemble_agent(model)
memory_agent = build_memory_agent(model)

gloss_agent_pipeline = Agent(
    name="gloss_agent_pipeline",
    model=model,
    description="A sequential pipeline agent that processes user requests through word, meaning, usage, and memory agents.",
    sub_agents=[word_agent, meaning_agent, usage_agent, assemble_agent, memory_agent],
)

print(f"✅ Pipeline Agent '{gloss_agent_pipeline.name}' created using model '{gloss_agent_pipeline.model}' with sub-agents: {[sa.name for sa in gloss_agent_pipeline.sub_agents]}")


root_agent = gloss_agent_pipeline