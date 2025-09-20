# Orion4D_MasterPrompt/text_prompt_mixer.py
# MP • Text Prompt Mixer — assemble plusieurs champs texte (ou entrées externes)
# avec un séparateur PAR LIGNE. Options: trim/skip_empty/collapse_blank_lines + pré/suffixe globaux.

import json
from typing import Any, Dict

CATEGORY = "MasterPrompt"
MAX_FIELDS = 12  # borne dure d'entrées externes


def _opt_inputs_dict():
    opt: Dict[str, Any] = {}
    for i in range(1, MAX_FIELDS + 1):
        opt[f"ext_text_{i}"] = ("STRING", {"default": "", "forceInput": True, "multiline": True})
    opt.update({
        "add_prefix": ("BOOLEAN", {"default": False}),
        "custom_prefix": ("STRING", {"default": "", "multiline": True}),
        "add_suffix": ("BOOLEAN", {"default": False}),
        "custom_suffix": ("STRING", {"default": "", "multiline": True}),
    })
    return opt


def _unescape(s: str) -> str:
    """Interprète \n, \t, \\ saisis dans l'UI."""
    return s.replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")


class TextPromptMixer:
    """
    - UI (JS): lignes: enabled + text + sep (séparateur par ligne).
    - ext_text_1..12 remplace 'text' de la ligne i quand fourni.
    - Assemblage déterministe: on insère le sep de la LIGNE i entre i et i+1 (pas de sep final).
    - 'config_json':
      [
        {"enabled": true, "text": "A", "sep": ", "},
        {"enabled": true, "text": "B", "sep": " | "}
      ]
    - Pas de 'max_items' : on utilise toutes les lignes présentes, bornées à MAX_FIELDS.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config_json": ("STRING", {"default": "[]", "multiline": True}),
                "skip_empty": ("BOOLEAN", {"default": True}),
                "trim_each": ("BOOLEAN", {"default": True}),
                "collapse_blank_lines": ("BOOLEAN", {"default": False}),
            },
            "optional": _opt_inputs_dict(),
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt_text", "parts_used")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def _collapse_blank_lines(self, s: str) -> str:
        lines = s.splitlines()
        out, blank = [], False
        for ln in lines:
            if ln.strip() == "":
                if not blank:
                    out.append("")
                blank = True
            else:
                out.append(ln)
                blank = False
        return "\n".join(out)

    def run(
        self,
        config_json: str,
        skip_empty: bool,
        trim_each: bool,
        collapse_blank_lines: bool,
        add_prefix: bool = False,
        custom_prefix: str = "",
        add_suffix: bool = False,
        custom_suffix: str = "",
        **ext_inputs,
    ):
        # 1) Parse config
        try:
            cfg = json.loads(config_json or "[]")
            if not isinstance(cfg, list):
                cfg = []
        except Exception:
            cfg = []
        for it in cfg:
            if isinstance(it, dict) and "sep" not in it:
                it["sep"] = ""

        # 2) Overrides externes (seulement 'text'), on étend la cfg si besoin (jusqu'à MAX_FIELDS)
        for i in range(1, MAX_FIELDS + 1):
            key = f"ext_text_{i}"
            val = ext_inputs.get(key, None)
            if isinstance(val, str) and val != "":
                if len(cfg) < i:
                    while len(cfg) < i:
                        cfg.append({"enabled": True, "text": "", "sep": ""})
                cfg[i - 1]["text"] = val

        # 3) Normalisation et sélection (on borne à MAX_FIELDS)
        pieces = []
        for item in cfg[:MAX_FIELDS]:
            if not isinstance(item, dict) or not bool(item.get("enabled", True)):
                continue
            txt = str(item.get("text", "") or "")
            sep = str(item.get("sep", "") or "")
            if trim_each:
                txt = txt.strip()
            if skip_empty and txt == "":
                continue
            pieces.append((txt, _unescape(sep)))

        # 4) Concat: sep de l'élément i entre i et i+1
        if not pieces:
            prompt, parts_used = "", 0
        else:
            out = [pieces[0][0]]
            for i in range(1, len(pieces)):
                out.append(pieces[i - 1][1])  # sep de la ligne précédente
                out.append(pieces[i][0])
            prompt, parts_used = "".join(out), len(pieces)

        # 5) Post
        if collapse_blank_lines:
            prompt = self._collapse_blank_lines(prompt)
        if add_prefix and custom_prefix:
            prompt = f"{custom_prefix}{prompt}"
        if add_suffix and custom_suffix:
            prompt = f"{prompt}{custom_suffix}"

        return (prompt, parts_used)


NODE_CLASS_MAPPINGS = {"text_prompt_mixer": TextPromptMixer}
NODE_DISPLAY_NAME_MAPPINGS = {"text_prompt_mixer": "MP • Text Prompt Mixer"}
