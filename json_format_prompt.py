# Orion4D_MasterPrompt/json_format_prompt.py
import json, ast

CATEGORY = "MasterPrompt"

def _parse_relaxed(obj_str: str):
    """Essaye JSON strict, sinon dict/list Python via ast.literal_eval."""
    s = (obj_str or "").strip()
    if not s:
        return None, "empty"
    try:
        return json.loads(s), ""
    except Exception as e_json:
        try:
            data = ast.literal_eval(s)
            return data, "parsed with literal_eval"
        except Exception as e_ast:
            return None, f"parse error: {e_json}"

def _stringify(data, pretty: bool, sort_keys: bool, ensure_ascii: bool, compact_one_line: bool):
    if compact_one_line:
        # compact au max, sans espaces inutiles
        return json.dumps(data, ensure_ascii=ensure_ascii, separators=(",", ":"), sort_keys=sort_keys)
    if pretty:
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=2, sort_keys=sort_keys)
    # défaut: minifié standard
    return json.dumps(data, ensure_ascii=ensure_ascii, separators=(",", ":"), sort_keys=sort_keys)

def _escape_for_prompt(s: str, escape_newlines: bool, escape_quotes: bool):
    out = s
    if escape_newlines:
        out = out.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")
    if escape_quotes:
        out = out.replace('"', '\\"')
    return out

class MPJsonFormat:
    """
    Entrée: json_in (objet/array en texte)
    Options:
      - pretty / sort_keys / ensure_ascii
      - compact_one_line (force 1 ligne)
      - escape_newlines / escape_quotes
      - wrap_backticks (```json ... ```)
    Sorties:
      - json_out (STRING)
      - diagnostic (STRING)
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_in": ("STRING", {"multiline": True, "default": ""}),
                "pretty": ("BOOLEAN", {"default": False}),
                "sort_keys": ("BOOLEAN", {"default": True}),
                "ensure_ascii": ("BOOLEAN", {"default": False}),
                "compact_one_line": ("BOOLEAN", {"default": False}),
                "escape_newlines": ("BOOLEAN", {"default": False}),
                "escape_quotes": ("BOOLEAN", {"default": False}),
                "wrap_backticks": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("json_out", "diagnostic")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self,
            json_in: str, pretty: bool, sort_keys: bool, ensure_ascii: bool,
            compact_one_line: bool, escape_newlines: bool, escape_quotes: bool,
            wrap_backticks: bool):
        data, diag = _parse_relaxed(json_in)
        if data is None:
            return ("", f"INVALID JSON - {diag}")

        out = _stringify(data, pretty, sort_keys, ensure_ascii, compact_one_line)
        if escape_newlines or escape_quotes:
            out = _escape_for_prompt(out, escape_newlines, escape_quotes)
        if wrap_backticks:
            out = f"```json\n{out}\n```"
        return (out, diag)

NODE_CLASS_MAPPINGS = {"mp_json_format": MPJsonFormat}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_json_format": "MP • JSON Format (Prompt)"}
