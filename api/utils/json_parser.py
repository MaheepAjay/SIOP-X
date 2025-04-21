import json
import re
from typing import Any

def clean_json_string(raw: str) -> str:
    """
    Clean up common issues in LLM-generated JSON:
    - Removes markdown (```json)
    - Fixes smart quotes
    - Removes trailing commas
    """
    cleaned = (
        raw.replace("```json", "")
           .replace("```", "")
           .replace("“", "\"")
           .replace("”", "\"")
           .replace("‘", "'")
           .replace("’", "'")
    )

    # Remove trailing commas inside JSON objects/lists
    cleaned = re.sub(r",(\s*[}\]])", r"\\1", cleaned)

    return cleaned.strip()

def safe_json_parse(raw: str, *, fallback: Any = None, verbose: bool = True) -> Any:
    """
    Attempts to parse JSON string safely.
    - Cleans common LLM formatting issues
    - Tries multiple fallbacks before giving up
    """
    if not raw or not isinstance(raw, str) or raw.strip() == "":
        if verbose:
            print("[JSON Parse Error] Received empty or non-string input")
        return fallback

    try:
        cleaned = clean_json_string(raw)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        if verbose:
            print(f"[JSON Parse Error] Original failed: {e}")
            print(f"[JSON Parse Error] Ra