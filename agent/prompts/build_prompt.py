"""Utilities for loading prompt files from the local prompts directory."""

from functools import lru_cache
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Use the directory containing this file as the prompts root so the module
# is importable and runnable from any CWD.
PROMPT_ROOT = Path(__file__).parent

@lru_cache(maxsize=128)
def load_prompt(*path_parts: str, encoding: str = "utf-8") -> str:
    """Load a prompt file (relative to `PROMPT_ROOT`) and return its text.

    Args:
        *path_parts: path components under `PROMPT_ROOT`, e.g. ("root", "identity.txt").
        encoding: file encoding to use when reading.

    Raises:
        FileNotFoundError: if the requested file doesn't exist.
    """
    path = PROMPT_ROOT.joinpath(*path_parts)
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path!s}")
    try:
        return path.read_text(encoding=encoding).strip()
    except Exception:
        logger.exception("Failed to read prompt file: %s", path)
        raise


def build_root_agent_prompt():
    parts = [
        load_prompt("root", "identity.txt"),
        load_prompt("root", "rules.txt"),
        load_prompt("root", "orchestration.txt"),
        load_prompt("shared", "taxonomy.txt"),
        load_prompt("shared", "response_templates.txt"),
    ]
    return "\n\n".join(parts)

def build_meaning_agent_prompt():
    parts = [
        load_prompt("meaning_agent", "identity.txt"),
        load_prompt("meaning_agent", "rules.txt"),
        load_prompt("shared", "taxonomy.txt"),
        load_prompt("meaning_agent", "output_contract.txt"),
        load_prompt("meaning_agent", "examples.txt"),
    ]
    return "\n\n".join(parts)

def build_usage_agent_prompt():
    parts = [
        load_prompt("usage_agent", "identity.txt"),
        load_prompt("usage_agent", "rules.txt"),
        load_prompt("shared", "taxonomy.txt"),
        load_prompt("usage_agent", "output_contract.txt"),
        load_prompt("usage_agent", "examples.txt"),
    ]
    return "\n\n".join(parts)

def build_memory_agent_prompt():
    parts = [
        load_prompt("memory_agent", "identity.txt"),
        load_prompt("memory_agent", "input_contract.txt"),
        load_prompt("memory_agent", "output_contract.txt"),
    ]
    return "\n\n".join(parts)