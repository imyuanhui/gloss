# import asyncio
# import json
# import uuid
# from typing import Any, Dict, Optional, Tuple

# from google.adk.agents.llm_agent import Agent
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# from tools.notion_connector import create_page  # your existing function

# from dotenv import load_dotenv
# import os

# load_dotenv()

# # =========================
# # 1) Prompts (single-file)
# # =========================

# MEANING_PROMPT = """
# You are the Gloss Meaning Agent.

# You receive a single user input intended to be a vocabulary lookup. The input may be:
# - a single word (e.g., "sport")
# - a short phrase (e.g., "sport a beard")
# - a word with a hint (e.g., "shrink meaning")

# Your job:
# 1) Normalize the lookup term.
# 2) Decide whether the input is ambiguous without context.
# 3) If ambiguous, return a meaning picker (2–4 options) and do NOT produce a final definition.
# 4) If not ambiguous (or if a sense is provided), produce exactly one core meaning sentence and classify it.

# You must return ONLY valid JSON. No markdown. No commentary.

# Input JSON schema:
# {
#   "user_input": string,
#   "selected_option": integer | null
# }

# - selected_option is null on the first pass.
# - If selected_option is provided, it refers to the option index from your previously returned meaning picker (1-based).

# Taxonomy:
# Meaning Type (pick exactly one):
# - Core Lexical
# - Cultural-Literacy
# - Polysemous Extension
# - Colloquial / Slang
# - Technical / Academic

# Domain (pick one or more):
# - Finance
# - Law
# - Housing
# - Psychology
# - Medicine
# - Technology
# - Culture / Media
# - Daily Life

# Ambiguity policy:
# - If multiple common senses exist and no clear context is present, ambiguity = "high".
# - If the user_input includes a collocation that strongly implies one sense (e.g., "sport a beard"), treat ambiguity as "low".
# - If you can infer a dominant sense with high confidence, treat ambiguity as "low".

# Output JSON schema (MUST be one of the following two forms):

# A) Meaning picker (when ambiguity is high):
# {
#   "status": "need_disambiguation",
#   "normalized_term": string,
#   "options": [string, string, ...]   // length 2–4
# }

# B) Final meaning (when ambiguity is low OR selected_option is provided):
# {
#   "status": "ok",
#   "normalized_term": string,
#   "sense_label": string,            // short, e.g. "sport (verb: display/wear)"
#   "core_meaning": string,           // exactly one sentence
#   "meaning_type": string,           // taxonomy value
#   "domain": [string, ...]           // 1+ taxonomy values
# }

# Rules for final meaning:
# - core_meaning must be one sentence, plain English, no examples, no lists.
# - Be decisive; avoid hedging ("may", "might", "can mean") in the final meaning form.
# - If classification is borderline, prefer:
#   Cultural-Literacy > Polysemous Extension > Technical / Academic > Colloquial / Slang > Core Lexical.
# """.strip()


# USAGE_PROMPT = """
# You are the Gloss Usage Agent.

# You receive a finalized meaning for a single term/phrase and produce practical usage guidance.

# You must return ONLY valid JSON. No markdown. No commentary.

# Input JSON schema:
# {
#   "normalized_term": string,
#   "sense_label": string,
#   "core_meaning": string,
#   "meaning_type": string,
#   "domain": [string, ...]
# }

# Output JSON schema:
# {
#   "usage_notes": string,
#   "example_sentence": string,
#   "related_words": [string, ...]
# }

# Rules:
# - usage_notes: 1–2 sentences. Focus on register (formal/informal), common patterns, and misuse risks.
# - example_sentence: exactly one sentence; must sound natural; no quotes; no parentheses.
# - related_words: 2–4 items; do not define them; prefer common near-synonyms or common co-occurrences.
# - Do not restate the definition. Add practical value.
# - If the term is slang/taboo, include a brief appropriateness warning inside usage_notes (one sentence max).
# """.strip()


# MEMORY_PROMPT = """
# You are the Gloss Memory Agent.

# Your sole responsibility is to transform structured vocabulary data into a Notion `properties` object for creating a new page.
# You do NOT call APIs. You do NOT judge success/failure. You do NOT add extra fields.

# You must return ONLY valid JSON. No markdown. No commentary.

# Input JSON schema:
# {
#   "word": string,
#   "sense_label": string,
#   "core_meaning": string,
#   "meaning_type": string,
#   "domain": [string, ...],
#   "usage_notes": string,
#   "example_sentence": string,
#   "related_words": [string, ...]
# }

# Output JSON schema:
# {
#   "notion_properties": { ... }
# }

# The `notion_properties` object MUST match this structure exactly:

# "Word / Phrase":
# { "title": [ { "text": { "content": "<word>" } } ] }

# "Core Meaning":
# { "rich_text": [ { "text": { "content": "<core_meaning>" } } ] }

# "Meaning Type":
# { "select": { "name": "<meaning_type>" } }

# "Domain":
# { "multi_select": [ { "name": "<domain1>" }, ... ] }

# "Usage Notes":
# { "rich_text": [ { "text": { "content": "<usage_notes>" } } ] }

# "Example":
# { "rich_text": [ { "text": { "content": "<example_sentence>" } } ] }

# "Related Words":
# - Join `related_words` with ", " into a single string.
# - Store as rich_text.
# - If `related_words` is empty, set "Related Words" to an empty rich_text array.

# Rules:
# - Trim whitespace in all string fields.
# - Preserve original casing of `word`.
# - If `domain` is empty, set it to ["Daily Life"].
# - Do not include any fields not listed above.
# """.strip()


# # =========================
# # 2) ADK helpers
# # =========================

# def _extract_final_text(event) -> Optional[str]:
#     try:
#         if event.is_final_response() and event.content and event.content.parts:
#             part0 = event.content.parts[0]
#             if getattr(part0, "text", None):
#                 return part0.text
#     except Exception:
#         pass
#     return None

# async def call_agent_for_text(
#     runner: Runner,
#     user_id: str,
#     session_id: str,
#     text: str,
# ) -> str:
#     # 1) Create session if it doesn't exist (ADK requires this)
#     session = await runner.session_service.get_session(
#         app_name=runner.app_name,
#         user_id=user_id,
#         session_id=session_id,
#     )
#     if session is None:
#         await runner.session_service.create_session(
#             app_name=runner.app_name,
#             user_id=user_id,
#             session_id=session_id,
#         )

#     # 2) Run agent
#     msg = types.Content(role="user", parts=[types.Part(text=text)])
#     final_text: Optional[str] = None

#     async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
#         maybe = _extract_final_text(event)
#         if maybe is not None:
#             final_text = maybe

#     if not final_text:
#         raise RuntimeError("No final response text received from agent.")
#     return final_text.strip()


# def parse_json_strict(text: str) -> Dict[str, Any]:
#     """
#     Parses JSON from model output. If the model accidentally outputs extra text,
#     tries to recover by extracting the first {...} block.
#     """
#     try:
#         return json.loads(text)
#     except json.JSONDecodeError:
#         # Recovery: extract first JSON object
#         start = text.find("{")
#         end = text.rfind("}")
#         if start != -1 and end != -1 and end > start:
#             return json.loads(text[start : end + 1])
#         raise


# # =========================
# # 3) Build agents + runners
# # =========================

# def build_gloss_agents(model: str = "gemini-2.5-flash") -> Tuple[Agent, Agent, Agent]:
#     meaning_agent = Agent(
#         model=model,
#         name="meaning_agent",
#         description="Resolves meaning; returns disambiguation options or final meaning JSON.",
#         instruction=MEANING_PROMPT,
#     )

#     usage_agent = Agent(
#         model=model,
#         name="usage_agent",
#         description="Produces usage notes, one example sentence, and related words as JSON.",
#         instruction=USAGE_PROMPT,
#     )

#     memory_agent = Agent(
#         model=model,
#         name="memory_agent",
#         description="Builds Notion properties JSON (no API calls).",
#         instruction=MEMORY_PROMPT,
#     )

#     return meaning_agent, usage_agent, memory_agent


# def build_runners(
#     meaning_agent: Agent,
#     usage_agent: Agent,
#     memory_agent: Agent,
#     app_name: str = "gloss",
# ) -> Tuple[Runner, Runner, Runner, InMemorySessionService]:
#     session_service = InMemorySessionService()

#     meaning_runner = Runner(agent=meaning_agent, app_name=app_name, session_service=session_service)
#     usage_runner = Runner(agent=usage_agent, app_name=app_name, session_service=session_service)
#     memory_runner = Runner(agent=memory_agent, app_name=app_name, session_service=session_service)

#     return meaning_runner, usage_runner, memory_runner, session_service


# # =========================
# # 4) The Python pipeline
# # =========================

# async def gloss_lookup(
#     user_input: str,
#     meaning_runner: Runner,
#     usage_runner: Runner,
#     memory_runner: Runner,
#     user_id: str = "local_user",
# ) -> Dict[str, Any]:
#     """
#     End-to-end pipeline:
#     1) Meaning resolution (may loop for disambiguation)
#     2) Usage generation
#     3) Memory serialization -> Notion properties
#     4) Python calls create_page(notion_properties)
#     """

#     # Use separate sessions per agent call to keep each call clean and avoid history bleed.
#     # (You can also reuse sessions if you want multi-turn agent memory.)
#     meaning_session_id = f"meaning-{uuid.uuid4().hex}"
#     usage_session_id = f"usage-{uuid.uuid4().hex}"
#     memory_session_id = f"memory-{uuid.uuid4().hex}"

#     # ---- Step 1: Meaning (loop if needed) ----
#     selected_option: Optional[int] = None
#     meaning: Dict[str, Any]

#     while True:
#         meaning_payload = {"user_input": user_input.strip(), "selected_option": selected_option}
#         meaning_text = await call_agent_for_text(
#             meaning_runner, user_id=user_id, session_id=meaning_session_id, text=json.dumps(meaning_payload)
#         )
#         meaning = parse_json_strict(meaning_text)

#         if meaning.get("status") == "ok":
#             break

#         if meaning.get("status") != "need_disambiguation":
#             raise RuntimeError(f"Meaning agent returned unexpected status: {meaning}")

#         options = meaning.get("options", [])
#         if not options or not isinstance(options, list):
#             raise RuntimeError(f"Meaning agent returned invalid options: {meaning}")

#         # In a real UI, you'd present these options and collect user choice.
#         # For CLI demo, we prompt:
#         print(f'\nAmbiguous term: "{meaning.get("normalized_term", user_input)}"')
#         for i, opt in enumerate(options, start=1):
#             print(f"{i}) {opt}")

#         selection = None

#         while selection is None:
#             raw = input(f"Select meaning (1-{len(options)}): ")  # may be str or dict depending on runtime

#             # If some runtime passes a dict, try common fields
#             if isinstance(raw, dict):
#                 raw = raw.get("selected_option") or raw.get("choice") or raw.get("selection")

#             # Now normalize to int
#             try:
#                 choice = int(raw)
#                 if 1 <= choice <= len(options):
#                     selection = choice
#                 else:
#                     print("Out of range. Try again.")
#             except (TypeError, ValueError):
#                 print("Invalid selection. Try again.")

#         selected_option = selection

#         # loop back to meaning_agent with selected_option

#     # ---- Step 2: Usage ----
#     usage_payload = {
#         "normalized_term": meaning["normalized_term"],
#         "sense_label": meaning["sense_label"],
#         "core_meaning": meaning["core_meaning"],
#         "meaning_type": meaning["meaning_type"],
#         "domain": meaning["domain"],
#     }

#     usage_text = await call_agent_for_text(
#         usage_runner, user_id=user_id, session_id=usage_session_id, text=json.dumps(usage_payload)
#     )
#     usage = parse_json_strict(usage_text)

#     # ---- Step 3: Memory serialization (Notion properties) ----
#     memory_payload = {
#         "word": meaning["normalized_term"],
#         "sense_label": meaning["sense_label"],
#         "core_meaning": meaning["core_meaning"],
#         "meaning_type": meaning["meaning_type"],
#         "domain": meaning["domain"],
#         "usage_notes": usage["usage_notes"],
#         "example_sentence": usage["example_sentence"],
#         "related_words": usage["related_words"],
#     }

#     memory_text = await call_agent_for_text(
#         memory_runner, user_id=user_id, session_id=memory_session_id, text=json.dumps(memory_payload)
#     )
#     memory = parse_json_strict(memory_text)

#     notion_properties = memory.get("notion_properties")
#     if not notion_properties or not isinstance(notion_properties, dict):
#         raise RuntimeError(f"Memory agent did not return notion_properties correctly: {memory}")

#     # ---- Step 4: Persist using your existing Python function ----
#     status_code = create_page(notion_properties)
#     saved = 200 <= int(status_code) < 300

#     # ---- Final response (you can format however you want) ----
#     result = {
#         "meaning": meaning,
#         "usage": usage,
#         "notion_properties": notion_properties,
#         "notion_status_code": status_code,
#         "saved": saved,
#     }
#     return result


# def format_user_response(meaning: Dict[str, Any], usage: Dict[str, Any], saved: bool) -> str:
#     domains = meaning.get("domain", [])
#     domains_str = " / ".join(domains) if isinstance(domains, list) else str(domains)

#     lines = [
#         f'{meaning.get("sense_label", meaning.get("normalized_term",""))}',
#         "",
#         "Meaning:",
#         meaning["core_meaning"],
#         "",
#         "How it’s used:",
#         usage["usage_notes"],
#         "",
#         "Type:",
#         f'{meaning["meaning_type"]} · {domains_str}',
#         "",
#         "Example:",
#         usage["example_sentence"],
#         "",
#         "✓ Saved to Gloss" if saved else "Saving failed — please try again.",
#     ]
#     return "\n".join(lines)


# # =========================
# # 5) CLI entry point
# # =========================

# async def main():
#     meaning_agent, usage_agent, memory_agent = build_gloss_agents()
#     meaning_runner, usage_runner, memory_runner, _ = build_runners(meaning_agent, usage_agent, memory_agent)

#     while True:
#         user_input = input("\nEnter a word/phrase (or 'quit'): ").strip()
#         if not user_input or user_input.lower() == "quit":
#             break

#         try:
#             result = await gloss_lookup(
#                 user_input=user_input,
#                 meaning_runner=meaning_runner,
#                 usage_runner=usage_runner,
#                 memory_runner=memory_runner,
#             )
#             print("\n" + format_user_response(result["meaning"], result["usage"], result["saved"]))
#         except Exception as e:
#             print(f"\nError: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())
