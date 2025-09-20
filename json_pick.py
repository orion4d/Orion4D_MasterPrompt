# Orion4D_MasterPrompt/json_pick.py
import json, ast, re
from typing import Any, List

CATEGORY = "MasterPrompt"

_PATH_TOKEN = re.compile(r"""
    (?:
        \.([A-Za-z_][A-Za-z0-9_]*)     # .key
      | \[([0-9]+)\]                   # [index]
    )
""", re.VERBOSE)

def _parse_relaxed(s: str):
    s = (s or "").strip()
    if not s:
        return None, "empty"
    try:
        return json.loads(s), ""
    except Exception as e:
        try:
            return ast.literal_eval(s), "parsed with literal_eval"
        except Exception as e2:
            return None, f"parse error: {e}"

def _get_path(obj: Any, path: str):
    # support: key1.key2[3].key3, clé initiale peut être sans point si le path commence direct par une clé
    cur = obj
    # normalise pour permettre "root.key" (facultatif).
    p = path.strip()
    if not p:
        return None, False
    # autorise première clé sans point
    if not p.startswith(".") and not p.startswith("["):
        p = "." + p
    for m in _PATH_TOKEN.finditer(p):
        key, idx = m.group(1), m.group(2)
        try:
            if key is not None:
                if not isinstance(cur, dict) or key not in cur:
                    return None, False
                cur = cur[key]
            else:
                if not isinstance(cur, list):
                    return None, False
                i = int(idx)
                if i < 0 or i >= len(cur):
                    return None, False
                cur = cur[i]
        except Exception:
            return None, False
    return cur, True

def _to_str(v: Any, stringify_json: bool):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False) if stringify_json else ""
    if v is None:
        return ""
    return str(v)

class MPJsonPick:
    """
    - json_in: objet/array
    - paths: liste de chemins (séparés par lignes) ex:
        title
        meta.author.name
        items[0].id
    - joiner: séparateur pour assembler les valeurs extraites
    - stringify_json: si True, les objets/arrays trouvés sont json.dumps() au lieu d'être vides
    Sorties: picked_text, hits_count
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_in": ("STRING", {"multiline": True, "default": ""}),
                "paths": ("STRING", {"multiline": True, "default": ""}),
                "joiner": ("STRING", {"default": "\n"}),
                "stringify_json": ("BOOLEAN", {"default": True}),
                "skip_empty": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("picked_text", "hits_count")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, json_in: str, paths: str, joiner: str, stringify_json: bool, skip_empty: bool):
        data, diag = _parse_relaxed(json_in)
        if data is None:
            return ("", 0)

        acc: List[str] = []
        hits = 0
        for raw in (paths or "").splitlines():
            p = raw.strip()
            if not p:
                continue
            val, ok = _get_path(data, p)
            s = _to_str(val, stringify_json) if ok else ""
            if s != "":
                acc.append(s)
                hits += 1
            elif not skip_empty:
                acc.append("")
        return (joiner.join(acc), hits)

NODE_CLASS_MAPPINGS = {"mp_json_pick": MPJsonPick}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_json_pick": "MP • JSON Pick (Paths → Text)"}
