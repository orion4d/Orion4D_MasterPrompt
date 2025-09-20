# Orion4D_MasterPrompt/json_kv_lines.py
# MP • JSON ↔︎ KV Lines — convertit un objet JSON <-> lignes "key: value"
# - kv_to_json : parse des lignes key: value (ou key = value) -> JSON
# - json_to_kv : aplatit un JSON en lignes key: value (chemins dot/brackets)
#
# Chemins supportés: a.b[2].c
# Commentaires: lignes commençant par # // ; (configurable)
# Doublons: last_wins | first_wins | to_array
# Coercion: true/false/null/nombres si activé
# Échappes: \n \t \\ dans les valeurs (option)

import json, ast, re
from typing import Any, Dict, List, Tuple

CATEGORY = "MasterPrompt"

_PATH_TOKEN = re.compile(r"""
    (?:
        \.([A-Za-z_][A-Za-z0-9_]*)     # .key
      | \[([0-9]+)\]                   # [index]
    )
""", re.VERBOSE)

def _unescape(s: str) -> str:
    return s.replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")

def _coerce(s: str) -> Any:
    t = s.strip()
    if t == "":
        return ""
    low = t.lower()
    if low == "true": return True
    if low == "false": return False
    if low in ("null", "none"): return None
    # nombres
    try:
        if re.fullmatch(r"[+-]?\d+", t):
            return int(t)
        if re.fullmatch(r"[+-]?\d+\.\d+", t):
            return float(t)
    except Exception:
        pass
    return t

def _parse_relaxed_json(text: str) -> Tuple[Any, str]:
    s = (text or "").strip()
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

def _ensure_path(root: Any, tokens: List[Any], dup_policy: str, value: Any):
    """
    Place 'value' à l'endroit désigné par tokens, en respectant dup_policy.
    tokens: ["a", "b", 2, "c"]  (indices -> int)
    """
    cur = root
    for i, tok in enumerate(tokens):
        last = (i == len(tokens) - 1)
        if isinstance(tok, str):  # dict key
            if last:
                if dup_policy == "first_wins" and tok in cur:
                    return
                if dup_policy == "to_array" and tok in cur:
                    old = cur[tok]
                    if isinstance(old, list):
                        old.append(value)
                        return
                    cur[tok] = [old, value]
                    return
                cur[tok] = value
                return
            if tok not in cur or not isinstance(cur[tok], (dict, list)):
                # si le prochain est int -> on crée une liste, sinon dict
                nxt = tokens[i + 1]
                cur[tok] = [] if isinstance(nxt, int) else {}
            cur = cur[tok]
        else:  # list index
            idx = int(tok)
            if not isinstance(cur, list):
                # transforme en liste
                cur_keys = []  # on écrase proprement
                cur = []
            # étend la liste si besoin
            while len(cur) <= idx:
                cur.append({})
            if last:
                # overwrite direct à l'index
                cur[idx] = value
                return
            # si l'élément n'est pas conteneur, prépare un dict/list selon le prochain token
            nxt = tokens[i + 1]
            if not isinstance(cur[idx], (dict, list)):
                cur[idx] = [] if isinstance(nxt, int) else {}
            cur = cur[idx]

def _parse_path(path: str) -> List[Any]:
    """
    "a.b[2].c" -> ["a","b",2,"c"]
    Autorise première clé sans point.
    """
    p = path.strip()
    if not p:
        return []
    if not p.startswith(".") and not p.startswith("["):
        p = "." + p
    tokens: List[Any] = []
    for m in _PATH_TOKEN.finditer(p):
        key, idx = m.group(1), m.group(2)
        if key is not None:
            tokens.append(key)
        else:
            tokens.append(int(idx))
    return tokens

def _flatten(obj: Any, base: str, items: List[Tuple[str, Any]], sort_keys: bool):
    if isinstance(obj, dict):
        keys = list(obj.keys())
        if sort_keys:
            keys.sort()
        for k in keys:
            kpath = f"{base}.{k}" if base else k
            _flatten(obj[k], kpath, items, sort_keys)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            kpath = f"{base}[{i}]" if base else f"[{i}]"
            _flatten(v, kpath, items, sort_keys)
    else:
        items.append((base, obj))

class MPJsonKVLines:
    """
    JSON ↔︎ KV Lines
    - mode: "kv_to_json" ou "json_to_kv"
    KV parsing:
      - sep_primary: séparateur principal (ex: ":")
      - allow_equals: autoriser '=' comme séparateur alternatif
      - comments: préfixes séparés par virgule (ex: "#,//,;")
      - coerce_types: True/False (true/false/null/nombres)
      - unescape_sequences: interpréter \\n \\t \\\\
      - duplicate_policy: last_wins | first_wins | to_array
    JSON flatten:
      - sort_keys: tri des clés pour stabilité
      - sep_out: séparateur à utiliser dans les lignes sorties (ex: ": ")
      - stringify_objects: si une feuille est un dict/list, json.dumps() (sinon on saute)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["kv_to_json", "json_to_kv"],),
                "text_in": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                # KV -> JSON
                "sep_primary": ("STRING", {"default": ":"}),
                "allow_equals": ("BOOLEAN", {"default": True}),
                "comments": ("STRING", {"default": "#,//,;"}),
                "coerce_types": ("BOOLEAN", {"default": True}),
                "unescape_sequences": ("BOOLEAN", {"default": True}),
                "duplicate_policy": (["last_wins", "first_wins", "to_array"],),
                # JSON -> KV
                "sort_keys": ("BOOLEAN", {"default": True}),
                "sep_out": ("STRING", {"default": ": "}),
                "stringify_objects": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text_out", "diagnostic")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    # ---------- KV -> JSON ----------
    def _kv_to_json(self, text: str, sep_primary: str, allow_equals: bool,
                    comments: str, coerce_types: bool, unescape_sequences: bool,
                    duplicate_policy: str) -> Tuple[str, str]:
        comment_prefixes = tuple([c.strip() for c in comments.split(",") if c.strip()])
        lines = text.splitlines()
        root: Dict[str, Any] = {}

        parsed = 0
        setcount = 0
        for raw in lines:
            s = raw.strip()
            if not s:  # vide
                continue
            if comment_prefixes and any(s.startswith(cp) for cp in comment_prefixes):
                continue

            # trouve le séparateur
            pos = s.find(sep_primary)
            pos_eq = s.find("=") if allow_equals else -1
            if allow_equals and (pos_eq != -1) and (pos == -1 or pos_eq < pos):
                pos = pos_eq
                sep_len = 1
            else:
                sep_len = len(sep_primary) if pos != -1 else -1

            if pos <= 0 or sep_len <= 0:
                # pas de sep valide -> on ignore proprement
                continue

            key = s[:pos].strip()
            val = s[pos + sep_len :].strip()

            if unescape_sequences:
                val = _unescape(val)

            if coerce_types:
                val_parsed = _coerce(val)
            else:
                val_parsed = val

            tokens = _parse_path(key) if key else []
            if not tokens:
                # clé plate (sans chemin) -> top-level string key
                tokens = [key]

            # s'assure que root est un dict
            if not isinstance(root, dict):
                root = {}

            _ensure_path(root, tokens, duplicate_policy, val_parsed)
            parsed += 1
            setcount += 1

        out = json.dumps(root, ensure_ascii=False, indent=2, sort_keys=True)
        diag = f"kv_to_json: parsed={parsed}, set={setcount}"
        return out, diag

    # ---------- JSON -> KV ----------
    def _json_to_kv(self, text: str, sort_keys: bool, sep_out: str,
                    stringify_objects: bool) -> Tuple[str, str]:
        data, diag = _parse_relaxed_json(text)
        if data is None:
            return "", f"INVALID JSON - {diag}"

        items: List[Tuple[str, Any]] = []
        _flatten(data, "", items, sort_keys=sort_keys)

        kv_lines: List[str] = []
        for k, v in items:
            if isinstance(v, (dict, list)):
                if not stringify_objects:
                    # on saute les conteneurs si demandé
                    continue
                kv_lines.append(f"{k}{sep_out}{json.dumps(v, ensure_ascii=False)}")
            elif v is None:
                kv_lines.append(f"{k}{sep_out}")
            else:
                kv_lines.append(f"{k}{sep_out}{v}")

        return "\n".join(kv_lines), f"json_to_kv: lines={len(kv_lines)}"

    # ---------- entry ----------
    def run(self, mode, text_in,
            sep_primary=":", allow_equals=True, comments="#,//,;",
            coerce_types=True, unescape_sequences=True, duplicate_policy="last_wins",
            sort_keys=True, sep_out=": ", stringify_objects=True):

        if mode == "kv_to_json":
            return self._kv_to_json(
                text_in, sep_primary, allow_equals, comments,
                coerce_types, unescape_sequences, duplicate_policy
            )

        # json_to_kv
        return self._json_to_kv(text_in, sort_keys, sep_out, stringify_objects)


NODE_CLASS_MAPPINGS = {"mp_json_kv_lines": MPJsonKVLines}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_json_kv_lines": "MP • JSON ↔︎ KV Lines"}
