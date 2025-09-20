# Orion4D_MasterPrompt/mp_wrap.py
CATEGORY = "MasterPrompt"

class MPWrap:
    PAIRS = {
        "Parentheses ()": ("(", ")"),
        "Brackets []": ("[", "]"),
        "Braces {}": ("{", "}"),
        "Quotes \"\"": ("\"", "\""),
        "Quotes ''": ("'", "'"),
        "Angles <>": ("<", ">"),
        "Guillemets « »": ("«", "»"),
        "Smart Quotes “ ”": ("“", "”"),
        "Chevrons ‹ ›": ("‹", "›"),
        "Custom": ("", ""),
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "style": (list(cls.PAIRS.keys()),),
                "per_line": ("BOOLEAN", {"default": True}),
                "trim_lines": ("BOOLEAN", {"default": True}),
                "space_inside": ("BOOLEAN", {"default": False}),  # ( text )
                "skip_if_empty": ("BOOLEAN", {"default": True}),
                "custom_prefix": ("STRING", {"default": ""}),
                "custom_suffix": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("wrapped_text",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self, text, style, per_line, trim_lines, space_inside, skip_if_empty, custom_prefix, custom_suffix):
        if style == "Custom":
            pre, suf = custom_prefix, custom_suffix
        else:
            pre, suf = self.PAIRS.get(style, ("", ""))

        def _wrap_one(s: str) -> str:
            if trim_lines:
                s = s.strip()
            if skip_if_empty and not s:
                return ""
            mid = f" {s} " if space_inside and s else s
            return f"{pre}{mid}{suf}"

        if not per_line:
            return (_wrap_one(text),)

        # par ligne (préserve les retours à la fin)
        lines = text.splitlines(keepends=False)
        wrapped = [_wrap_one(line) for line in lines]
        # si skip_if_empty, on garde des lignes vides si elles l'étaient déjà (pas d’ajout de paires)
        out_lines = []
        for orig, w in zip(lines, wrapped):
            out_lines.append(w if w != "" else (orig if orig == "" else ""))
        out = "\n".join(out_lines)
        return (out,)


NODE_CLASS_MAPPINGS = {"mp_wrap": MPWrap}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_wrap": "MP • Wrap (Pairs/Custom)"}
