import os
import re
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = None


def get_client():
    """Lazy-initialize the Gemini client. Works on both local and Streamlit Cloud."""
    global _client
    if _client is not None:
        return _client

    api_key = None

    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        pass

    # Fallback to environment variable
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. Set it in:\n"
            "  - .env file (local): GOOGLE_API_KEY=your_key\n"
            "  - Streamlit Cloud: App Settings → Secrets → GOOGLE_API_KEY = \"your_key\""
        )

    _client = genai.Client(api_key=api_key)
    return _client


def parse_json_response(text):
    """Robustly parse JSON from Gemini response, handling common issues.

    Handles:
    - Markdown code fences (```json ... ```)
    - Trailing commas
    - Single quotes instead of double quotes
    - Control characters in strings
    - Truncated JSON (attempts repair)
    """
    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        text = text.rsplit("```", 1)[0].strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Remove trailing commas before } or ]
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to fix truncated JSON by closing open brackets
    repaired = cleaned
    open_braces = repaired.count('{') - repaired.count('}')
    open_brackets = repaired.count('[') - repaired.count(']')

    # Remove any trailing partial string/key
    if open_braces > 0 or open_brackets > 0:
        # Trim back to last complete value
        repaired = re.sub(r',\s*"[^"]*$', '', repaired)  # partial key
        repaired = re.sub(r',\s*$', '', repaired)  # trailing comma
        repaired += ']' * open_brackets + '}' * open_braces

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Last resort: find the largest valid JSON object/array in the text
    for match in re.finditer(r'[\[{]', text):
        start = match.start()
        bracket = '}' if text[start] == '{' else ']'
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            c = text[i]
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c in '{[':
                depth += 1
            elif c in '}]':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"Could not parse JSON from Gemini response. Raw text:\n{text[:500]}")
