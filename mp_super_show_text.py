# Orion4D_MasterPrompt/mp_super_show_text.py
# MP • Super Show Text — affiche un texte (chaîne OU chemin .txt/.csv),
# numérote (option), et extrait des lignes par numéro/plage. Aperçu dans le node.

import os, io, re
from typing import List, Optional

CATEGORY = "MasterPrompt"

def _annotate_lines(txt: str, prefix: str, suffix: str, space: bool) -> str:
    lines = txt.splitlines()
    sp = " " if space else ""
    return "\n".join(f"{prefix}{i}{suffix}{sp}{line}" for i, line in enumerate(lines, start=1))

def _parse_line_selector(selector: str, total: int) -> List[int]:
    """1-based; supporte '3', '1-10', '1,2,6,53', '1-3,7,10-12'."""
    if not selector:
        return []
    # normaliser les tirets unicode éventuels vers '-' ASCII
    selector = selector.replace("–", "-").replace("—", "-").replace("−", "-")
    s = re.sub(r"[^0-9,\-\s]", "", selector)

    out = set()
    for token in s.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-", 1)
            if a.isdigit() and b.isdigit():
                start, end = int(a), int(b)
                if start > end:  # tolérer "30-23"
                    start, end = end, start
                start = max(1, start)
                end = min(total, end)
                if start <= end:
                    out.update(range(start, end + 1))
        else:
            if token.isdigit():
                k = int(token)
                if 1 <= k <= total:
                    out.add(k)
    return sorted(out)

def _read_text_file_if_path(maybe_path: str) -> Optional[str]:
    if not isinstance(maybe_path, str):
        return None
    p = maybe_path.strip()
    if not p or not os.path.isfile(p):
        return None
    ext = os.path.splitext(p)[1].lower()
    if ext not in {".txt", ".csv"}:
        return None
    try:
        with io.open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        try:
            with open(p, "rb") as f:
                return f.read().decode("utf-8", errors="replace")
        except Exception:
            return None

class MPSuperShowText:
    """
    Entrées:
      - text (STRING, forceInput=True) : texte ou chemin .txt/.csv
      - show_numbers (bool)
      - num_prefix / num_suffix (string)  ← robustifiés si le cache envoie des bool
      - num_space (bool)
      - line_selector (string)            : "3" | "1-10" | "1,2,6,53" | "1-3,7,10-12"
    Sorties:
      - text_out      : texte complet (numéroté si show_numbers=True)
      - selected_text : lignes sélectionnées (sans renumérotation)
    """
    OUTPUT_NODE = True   # autorise l’exécution sans rien brancher en sortie

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "show_numbers": ("BOOLEAN", {"default": True}),
                "num_prefix": ("STRING", {"default": "(", "multiline": False}),
                "num_suffix": ("STRING", {"default": ")", "multiline": False}),
                "num_space": ("BOOLEAN", {"default": True}),
                "line_selector": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": "ex: 3  |  1-10  |  1,2,6,53  |  1-3,7,10-12",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text_out", "selected_text")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, text, show_numbers, num_prefix, num_suffix, num_space, line_selector):
        # 1) texte brut ou chemin de fichier
        raw = text if isinstance(text, str) else str(text or "")
        file_text = _read_text_file_if_path(raw)
        base_text = file_text if file_text is not None else raw

        # 2) robustesse contre le cache (si Comfy renvoie des bool par erreur)
        if not isinstance(num_prefix, str):
            num_prefix = "("
        if not isinstance(num_suffix, str):
            num_suffix = ")"
        num_space = bool(num_space)
        show_numbers = bool(show_numbers)

        # 3) rendu principal
        display_text = (
            _annotate_lines(base_text, num_prefix, num_suffix, num_space)
            if show_numbers else base_text
        )

        # 4) extraction des lignes
        lines = base_text.splitlines()
        idx = _parse_line_selector(line_selector, len(lines))
        selected_text = "\n".join(lines[i - 1] for i in idx) if idx else ""

        return {
            "ui": {"text": display_text},
            "result": (display_text, selected_text),
        }

NODE_CLASS_MAPPINGS = {"mp_super_show_text": MPSuperShowText}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_super_show_text": "MP • Super Show Text"}
