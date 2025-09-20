# Orion4D_MasterPrompt/multi_list_mixer.py
import json
import random

# On réutilise les helpers du node existant
from .list_selector_pro import (
    PKG_NAME, _is_safe_rel_path, _safe_join, _read_lines
)

CATEGORY = "MasterPrompt"


class MultiListMixer:
    """
    Multi List Mixer
    - UI dynamique côté JS : plusieurs (folder, file, temperature[0..10])
    - Tirage pondéré par 'temperature' pour choisir le fichier
    - Puis tirage d'une ligne dans ce fichier (seedé)
    - Pré/suffixes optionnels
    - 'config_json' est un tableau JSON d'objets:
      [{ "folder": "sub/dir", "file": "sub/dir/list.txt", "temperature": 7 }, ...]
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Le JS remplit ce champ (masqué côté UI) avec la config des lignes
                "config_json": ("STRING", {"default": "[]", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "add_prefix": ("BOOLEAN", {"default": False}),
                "custom_prefix": ("STRING", {"default": "", "multiline": True}),
                "add_suffix": ("BOOLEAN", {"default": False}),
                "custom_suffix": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("mixed_text",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def _pick_weighted_file(self, entries, rrandom):
        """
        entries: [{file, temperature}, ...] déjà validés.
        Choisit un 'file' selon poids = temperature (0 ignoré).
        """
        pool = [(e["file"], max(0.0, float(e.get("temperature", 0)))) for e in entries]
        pool = [(f, w) for (f, w) in pool if w > 0]
        if not pool:
            return None

        total = sum(w for _, w in pool)
        x = rrandom.random() * total
        acc = 0.0
        for f, w in pool:
            acc += w
            if x <= acc:
                return f
        return pool[-1][0]

    def run(
        self,
        config_json,
        seed,
        add_prefix=False, custom_prefix="",
        add_suffix=False, custom_suffix=""
    ):
        # 1) Parse config venant du JS
        try:
            cfg = json.loads(config_json or "[]")
        except Exception:
            cfg = []

        # 2) Valide / sécurise
        valid = []
        for item in cfg if isinstance(cfg, list) else []:
            file_rel = (item.get("file") or "").strip()
            try:
                if not file_rel or not _is_safe_rel_path(file_rel):
                    continue
                full = _safe_join(file_rel)
                lines = _read_lines(full)
                if not lines:
                    continue
                valid.append({
                    "file": file_rel,
                    "temperature": float(item.get("temperature", 0)),
                    "lines": lines
                })
            except Exception as e:
                print(f"[{PKG_NAME}] skip entry {file_rel}: {e}")

        if not valid:
            return ("",)

        # 3) RNG local et tirage pondéré du fichier
        rrandom = random.Random(seed)
        chosen_file = self._pick_weighted_file(valid, rrandom)
        if not chosen_file:
            return ("",)

        # 4) Retrouve les lignes du fichier choisi
        lines = None
        for v in valid:
            if v["file"] == chosen_file:
                lines = v["lines"]
                break
        if not lines:
            return ("",)

        # 5) Choisit une ligne
        base = rrandom.choice(lines)

        # 6) Pré/Suffix
        out = f"{custom_prefix if add_prefix else ''}{base}{custom_suffix if add_suffix else ''}"
        return (out,)


NODE_CLASS_MAPPINGS = {
    "multi_list_mixer": MultiListMixer,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "multi_list_mixer": "MP • Multi List Mixer"
}
