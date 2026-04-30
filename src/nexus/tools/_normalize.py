import ast


def extract_str(val: object) -> str:
    """Normalize tool arguments from llama3.2 marshaling quirks.

    Handles three observed formats:
      1. Plain string:                "docs/perfil"
      2. JSON schema dict:            {"type": "string", "value": "docs/perfil"}
      3. Stringified Python dict:     "{'path': 'docs/perfil'}"
    """
    if isinstance(val, dict):
        return str(val.get("value", val.get("text", next(iter(val.values()), ""))))
    if isinstance(val, str):
        stripped = val.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                parsed = ast.literal_eval(stripped)
                if isinstance(parsed, dict):
                    return str(next(iter(parsed.values()), val))
            except (ValueError, SyntaxError):
                pass
    return str(val)
