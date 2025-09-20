# Orion4D_MasterPrompt/json_merge.py
import json, ast
from typing import Any, Dict, List

CATEGORY = "MasterPrompt"

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

def _deep_merge(a: Any, b: Any, array_policy: str):
    # b écrase/complète a
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = _deep_merge(a.get(k), v, array_policy) if k in a else v
        return out
    if isinstance(a, list) and isinstance(b, list):
        if array_policy == "replace":
            return list(b)
        if array_policy == "concat":
            return list(a) + list(b)
        if array_policy == "unique":
            seen = set()
            res = []
            for x in list(a) + list(b):
                key = json.dumps(x, sort_keys=True) if isinstance(x, (dict, list)) else str(x)
                if key not in seen:
                    seen.add(key)
                    res.append(x)
            return res
    # par défaut: b remplace a
    return b if b is not None else a

class MPJsonMerge:
    """
    Fusion profonde de plusieurs objets JSON.
    - Priorité de gauche à droite: base <- j2 <- j3 ...
    - array_policy: replace | concat | unique
    - remove_nulls: si True, enlève toutes les clés à valeur None/null après fusion
    """
    @classmethod
    def INPUT_TYPES(cls):
        opt = {f"json_{i}": ("STRING", {"multiline": True, "default": ""}) for i in range(1, 6)}
        return {
            "required": {
                "array_policy": (["replace", "concat", "unique"],),
                "remove_nulls": ("BOOLEAN", {"default": False}),
                "pretty": ("BOOLEAN", {"default": False}),
                "sort_keys": ("BOOLEAN", {"default": True}),
            },
            "optional": opt,
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("json_merged", "diagnostic")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def _remove_nulls(self, o):
        if isinstance(o, dict):
            return {k: self._remove_nulls(v) for k, v in o.items() if v is not None}
        if isinstance(o, list):
            return [self._remove_nulls(x) for x in o]
        return o

    def run(self, array_policy, remove_nulls, pretty, sort_keys, **json_inputs):
        diags: List[str] = []
        objs: List[Dict] = []

        for i in range(1, 6):
            s = json_inputs.get(f"json_{i}", "")
            if not s:
                continue
            data, d = _parse_relaxed(s)
            if d: diags.append(f"json_{i}: {d}")
            if data is None:
                continue
            if not isinstance(data, (dict, list)):
                diags.append(f"json_{i}: not an object/array")
            objs.append(data)

        if not objs:
            return ("", "no input")

        merged = objs[0]
        for nxt in objs[1:]:
            merged = _deep_merge(merged, nxt, array_policy)

        if remove_nulls:
            merged = self._remove_nulls(merged)

        if pretty:
            out = json.dumps(merged, indent=2, sort_keys=sort_keys, ensure_ascii=False)
        else:
            out = json.dumps(merged, separators=(",", ":"), sort_keys=sort_keys, ensure_ascii=False)

        return (out, "; ".join(diags))

NODE_CLASS_MAPPINGS = {"mp_json_merge": MPJsonMerge}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_json_merge": "MP • JSON Merge (Deep)"}
