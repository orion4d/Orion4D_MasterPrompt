# Orion4D_MasterPrompt/mp_format.py
import json, re, ast

CATEGORY = "MasterPrompt"

class MPFormat:
    @classmethod
    def INPUT_TYPES(cls):
        optional_inputs = {f"arg_{i}": ("STRING", {"forceInput": True}) for i in range(10)}
        optional_inputs.update({
            "kwargs_json": ("STRING", {"multiline": True, "default": ""}),
            "policy": (["strict", "skip-missing", "default-empty"],),
        })
        return {
            "required": {
                "format_string": ("STRING", {"multiline": True, "default": "Hello {name}, meet {0}."}),
            },
            "optional": optional_inputs,
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text_out", "diagnostic")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def _parse_kwargs(self, s: str):
        s = (s or "").strip()
        if not s:
            return {}, ""
        # 1) JSON strict
        try:
            data = json.loads(s)
            if isinstance(data, dict):
                return {str(k): "" if v is None else str(v) for k, v in data.items()}, ""
            return {}, "kwargs_json must be a JSON object"
        except Exception as e1:
            # 2) Tolérance: dict Python via ast.literal_eval ({'name': 'Alice'})
            try:
                data = ast.literal_eval(s)
                if isinstance(data, dict):
                    return {str(k): "" if v is None else str(v) for k, v in data.items()}, "parsed with literal_eval"
                return {}, "kwargs_json must be an object"
            except Exception as e2:
                return {}, f"bad kwargs_json: {e1}"

    def run(self, format_string, policy="default-empty", kwargs_json="", **positional):
        # positionnels
        args = [positional.get(f"arg_{i}", "") for i in range(10)]

        # nommés
        kwargs, diag = self._parse_kwargs(kwargs_json)

        # placeholders nommés présents
        keys_in_template = set(re.findall(r"{([a-zA-Z_][a-zA-Z0-9_]*)}", format_string))
        missing_named = [k for k in keys_in_template if k not in kwargs]

        # stratégie de gestion des manquants
        if policy == "skip-missing" and missing_named:
            tmp = format_string
            for k in missing_named:
                tmp = tmp.replace("{"+k+"}", "")
            try:
                out = tmp.format(*args, **kwargs)
                diag2 = ("; " if diag else "") + (f"missing: {', '.join(missing_named)}" if missing_named else "")
                return (out, (diag + diag2).strip("; ").strip())
            except Exception as e2:
                return (f"FORMAT ERROR: {e2}", (diag + f"; skip-missing failed: {e2}").strip("; ").strip())

        if policy == "default-empty" and missing_named:
            fill = {k: "" for k in missing_named}
            try:
                out = format_string.format(*args, **({**kwargs, **fill}))
                diag2 = ("; " if diag else "") + (f"auto-empty: {', '.join(missing_named)}" if missing_named else "")
                return (out, (diag + diag2).strip("; ").strip())
            except Exception as e3:
                return (f"FORMAT ERROR: {e3}", (diag + f"; default-empty failed: {e3}").strip("; ").strip())

        # strict (ou aucun manquant)
        try:
            out = format_string.format(*args, **kwargs)
            return (out, diag)
        except (KeyError, IndexError) as e:
            if policy == "strict":
                return (f"FORMAT ERROR: {e}", (diag + f"; strict: {e}").strip("; ").strip())
            # par sécurité, si on arrive ici, renvoyer l’erreur
            return (f"FORMAT ERROR: {e}", (diag + f"; error: {e}").strip("; ").strip())


NODE_CLASS_MAPPINGS = {"mp_format": MPFormat}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_format": "MP • Format (Named/Indexed)"}
