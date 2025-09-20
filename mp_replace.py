# Orion4D_MasterPrompt/mp_replace.py
import json, re

CATEGORY = "MasterPrompt"

class MPReplace:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "mode": (["simple", "regex"],),
                "find": ("STRING", {"multiline": False, "default": ""}),
                "replace": ("STRING", {"multiline": False, "default": ""}),
                "scope": (["all", "first"],),
                "ignore_case": ("BOOLEAN", {"default": False}),
                "multiline": ("BOOLEAN", {"default": False}),
                "dotall": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                # Si fourni (non vide), applique une table de remplacements (JSON objet)
                # ex: {"foo":"bar", "hello":"world"} — traités en mode "simple", ordre stable par clés triées
                "table_json": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text_out", "replacements")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def _apply_simple(self, text, find, repl, scope, ignore_case):
        if not find:
            return text, 0
        if ignore_case:
            # remplace insensible à la casse en mode simple
            pattern = re.compile(re.escape(find), re.IGNORECASE)
            count = 0 if scope == "all" else 1
            new, n = pattern.subn(repl, text, count=count)
            return new, n
        else:
            if scope == "first":
                # str.replace(count=1)
                new = text.replace(find, repl, 1)
                n = 1 if new != text else 0
                return new, n
            else:
                new = text.replace(find, repl)
                # compter les occurrences naïvement
                n = text.count(find)
                return new, n

    def _apply_regex(self, text, find, repl, scope, ignore_case, multiline, dotall):
        if not find:
            return text, 0
        flags = 0
        if ignore_case: flags |= re.IGNORECASE
        if multiline:   flags |= re.MULTILINE
        if dotall:      flags |= re.DOTALL
        pattern = re.compile(find, flags)
        count = 0 if scope == "all" else 1
        new, n = pattern.subn(repl, text, count=count)
        return new, n

    def _apply_table(self, text, table_str):
        try:
            table = json.loads(table_str)
            if not isinstance(table, dict):
                return text, 0
        except Exception:
            return text, 0
        # ordre prédictible
        total = 0
        for k in sorted(table.keys()):
            v = str(table[k])
            if not k:
                continue
            # simple, sensible à la casse
            c = text.count(k)
            if c:
                text = text.replace(k, v)
                total += c
        return text, total

    def run(self, text, mode, find, replace, scope, ignore_case, multiline, dotall, table_json=""):
        # Table JSON prioritaire si non vide
        table_json = (table_json or "").strip()
        if table_json:
            out, n = self._apply_table(text, table_json)
            return (out, n)

        if mode == "regex":
            out, n = self._apply_regex(text, find, replace, scope, ignore_case, multiline, dotall)
        else:
            out, n = self._apply_simple(text, find, replace, scope, ignore_case)
        return (out, n)


NODE_CLASS_MAPPINGS = {"mp_replace": MPReplace}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_replace": "MP • Replace (Simple/Regex)"}
