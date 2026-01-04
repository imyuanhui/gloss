import json
from typing import Any

def extract_json(text: str) -> Any:
    """
    Extract the first valid JSON object/array from a string.
    Robust against leading/trailing text and braces in explanations.
    """
    if not text:
        raise ValueError("Empty text")

    decoder = json.JSONDecoder()
    s = text.strip()

    # Try from every position where JSON could start
    for i, ch in enumerate(s):
        if ch not in "{[":
            continue
        try:
            obj, end = decoder.raw_decode(s[i:])
            return obj
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError("No valid JSON found", s, 0)