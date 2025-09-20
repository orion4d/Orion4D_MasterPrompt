# Orion4D_MasterPrompt/text_field_mixer.py
import json, random
from typing import Any, Dict

PKG_NAME = "Orion4D_MasterPrompt"
CATEGORY = "MasterPrompt"
MAX_FIELDS = 12  # nombre max de champs gérés par des entrées externes


def _opt_inputs_dict():
    """
    Construit le dict 'optional' pour INPUT_TYPES en respectant l'ordre d'insertion.
    On expose d'abord les entrées externes ext_text_1..N (STRING, forceInput),
    puis les options prefix/suffix (comme Multi List Mixer).
    """
    opt: Dict[str, Any] = {}
    for i in range(1, MAX_FIELDS + 1):
        opt[f"ext_text_{i}"] = ("STRING", {"default": "", "forceInput": True, "multiline": True})
    opt["add_prefix"] = ("BOOLEAN", {"default": False})
    opt["custom_prefix"] = ("STRING", {"default": "", "multiline": True})
    opt["add_suffix"] = ("BOOLEAN", {"default": False})
    opt["custom_suffix"] = ("STRING", {"default": "", "multiline": True})
    return opt


class TextFieldMixer:
    """
    Text Field Mixer
    - UI (JS): lignes dynamiques (enabled, text via modale ✏️, temperature[0..10])
    - Entrées externes: ext_text_1..ext_text_12 (optionnelles). Si connecté/non-vide,
      le texte externe remplace celui du champ i et l'édition est désactivée côté UI.
    - Tirage pondéré parmi les champs 'enabled' avec poids = température (seedé).
    - Pré/Suffix en option, en bas du node.
    - 'config_json' garde l'état côté UI :
      [
        {"enabled": true, "text": "foo", "temperature": 7},
        ...
      ]
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config_json": ("STRING", {"default": "[]", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": _opt_inputs_dict(),
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("mixed_text",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def _weighted_pick(self, entries, rrandom: random.Random):
        pool = []
        for e in entries:
            txt = (e.get("text") or "").strip()
            if not txt:
                continue
            if not bool(e.get("enabled", True)):
                continue
            try:
                w = float(e.get("temperature", 0.0))
            except Exception:
                w = 0.0
            w = max(0.0, min(10.0, w))
            if w > 0.0:
                pool.append((txt, w))

        if not pool:
            return None

        total = sum(w for _, w in pool)
        x = rrandom.random() * total
        acc = 0.0
        for txt, w in pool:
            acc += w
            if x <= acc:
                return txt
        return pool[-1][0]

    def run(
        self,
        config_json,
        seed,
        add_prefix=False,
        custom_prefix="",
        add_suffix=False,
        custom_suffix="",
        **ext_inputs,  # ext_text_1..ext_text_N arriveront ici
    ):
        # 1) Parse UI config
        try:
            cfg = json.loads(config_json or "[]")
            if not isinstance(cfg, list):
                cfg = []
        except Exception as e:
            print(f"[{PKG_NAME}] TextFieldMixer: bad JSON: {e}")
            cfg = []

        # 2) Applique les overrides externes
        #    Pour chaque i, si ext_text_i non vide -> remplace 'text' de la ligne i-1.
        for i in range(1, MAX_FIELDS + 1):
            key = f"ext_text_{i}"
            val = ext_inputs.get(key, None)
            if val is None:
                continue
            # Comfy passe souvent des STRING en str; si non connecté, c'est "" (default)
            if isinstance(val, str) and val != "":
                # s'assurer que la ligne existe
                if len(cfg) < i:
                    # complète avec des lignes neutres jusqu'à i
                    while len(cfg) < i:
                        cfg.append({"enabled": True, "text": "", "temperature": 5})
                # remplace seulement le texte (on garde enabled/temperature de l'UI)
                cfg[i - 1]["text"] = val

        # 3) Tirage seedé
        r = random.Random(seed)
        picked = self._weighted_pick(cfg, r)
        if picked is None:
            return ("",)

        # 4) Pré/Suffix
        if add_prefix:
            picked = f"{custom_prefix}{picked}"
        if add_suffix:
            picked = f"{picked}{custom_suffix}"

        return (picked,)


NODE_CLASS_MAPPINGS = {"text_field_mixer": TextFieldMixer}
NODE_DISPLAY_NAME_MAPPINGS = {"text_field_mixer": "MP • Text Field Mixer"}
