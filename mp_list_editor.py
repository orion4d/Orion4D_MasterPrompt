# Orion4D_MasterPrompt/mp_list_editor.py
# MP • List Editor — édite/retouche des listes + enregistre dans ComfyUI/output/<subfolder>
import os
import re
from typing import List, Tuple

CATEGORY = "MasterPrompt"


def _sanitize_token(s: str, default: str) -> str:
    """Garde un token sûr pour nom de fichier/dossier (sans traversal)."""
    s = (s or "").strip()
    if not s:
        return default
    s = re.sub(r"\s+", "_", s)                      # espaces -> _
    s = re.sub(r"[^a-zA-Z0-9._-]", "", s)           # caractères sûrs
    return s or default


def _sanitize_basename(name: str, default: str = "edited_list") -> str:
    name = os.path.basename(name or "").strip()
    name = _sanitize_token(name, default)
    # retire extension si donnée par l'utilisateur
    name = re.sub(r"\.(txt|csv)$", "", name, flags=re.IGNORECASE)
    return name


def _sanitize_subfolder(path_like: str, default: str = "List_modified") -> str:
    """
    Autorise une hiérarchie simple "foo/bar" en nettoyant chaque segment,
    et en bloquant toute tentative de traversal.
    """
    if not path_like:
        return default
    segments = re.split(r"[\\/]+", path_like.strip())
    safe = [_sanitize_token(seg, "") for seg in segments if seg.strip()]
    return os.path.join(*(seg for seg in safe if seg)) or default


class MPListEditor:
    """
    Pipeline :
      1) Find/Replace (ligne par ligne ou global)
      2) Edit par ligne (couper/ajouter pré/suffixe)
      3) Remove blanks
      4) Dedupe
      5) Sort
      6) Join + Save optionnel (ComfyUI/output/<subfolder>/<basename>.txt|.csv)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Source
                "text_in": ("STRING", {"multiline": True, "default": ""}),

                # Find/Replace
                "find_replace_mode": (["none", "simple", "regex"],),
                "find": ("STRING", {"default": ""}),
                "replace": ("STRING", {"default": ""}),
                "scope": (["all", "first"],),
                "ignore_case": ("BOOLEAN", {"default": True}),
                "multiline": ("BOOLEAN", {"default": False}),
                "dotall": ("BOOLEAN", {"default": False}),
                "apply_per_line": ("BOOLEAN", {"default": True}),

                # Nettoyage
                "remove_blank_lines": ("BOOLEAN", {"default": True}),
                "remove_duplicates": ("BOOLEAN", {"default": True}),

                # Tri
                "sort_alpha": ("BOOLEAN", {"default": True}),
                "descending": ("BOOLEAN", {"default": False}),
                "case_insensitive": ("BOOLEAN", {"default": True}),

                # Edit par ligne
                "remove_prefix_chars": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "remove_suffix_chars": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "add_prefix": ("STRING", {"default": ""}),
                "add_suffix": ("STRING", {"default": ""}),

                # Save (toujours dans ComfyUI/output/<subfolder>)
                "save_output": ("BOOLEAN", {"default": False}),
                "subfolder": ("STRING", {"default": "List_modified"}),
                "file_basename": ("STRING", {"default": "edited_list"}),
                "save_format": (["txt", "csv"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text_out", "saved_path")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    # ---------- Find/Replace helpers ----------
    def _simple_replace(self, text: str, find: str, repl: str, scope: str, ignore_case: bool) -> Tuple[str, int]:
        if not find:
            return text, 0
        if ignore_case:
            pat = re.compile(re.escape(find), re.IGNORECASE)
            count = 0 if scope == "all" else 1
            new, n = pat.subn(repl, text, count=count)
            return new, n
        else:
            if scope == "first":
                new = text.replace(find, repl, 1)
                return new, 1 if new != text else 0
            new = text.replace(find, repl)
            return new, text.count(find)

    def _regex_replace(self, text: str, find: str, repl: str, scope: str,
                       ignore_case: bool, multiline: bool, dotall: bool) -> Tuple[str, int]:
        if not find:
            return text, 0
        flags = 0
        if ignore_case: flags |= re.IGNORECASE
        if multiline:   flags |= re.MULTILINE
        if dotall:      flags |= re.DOTALL
        pat = re.compile(find, flags)
        count = 0 if scope == "all" else 1
        new, n = pat.subn(repl, text, count=count)
        return new, n

    def _apply_find_replace_text(self, content: str, mode: str, find: str, repl: str,
                                 scope: str, ignore_case: bool, multiline: bool, dotall: bool) -> Tuple[str, int]:
        if mode == "simple":
            return self._simple_replace(content, find, repl, scope, ignore_case)
        elif mode == "regex":
            return self._regex_replace(content, find, repl, scope, ignore_case, multiline, dotall)
        return content, 0

    # ---------- Line helpers ----------
    def _edit_line(self, line: str, rem_pre_n: int, rem_suf_n: int, add_pre: str, add_suf: str) -> str:
        s = line
        if rem_pre_n > 0:
            s = s[rem_pre_n:] if len(s) > rem_pre_n else ""
        if rem_suf_n > 0:
            s = s[:-rem_suf_n] if len(s) > rem_suf_n else ""
        if add_pre:
            s = f"{add_pre}{s}"
        if add_suf:
            s = f"{s}{add_suf}"
        return s

    def _dedupe_keep_order(self, items: List[str]) -> List[str]:
        seen = set()
        out = []
        for x in items:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out

    def _resolve_output_dir(self, subfolder: str) -> str:
        """Retourne ComfyUI/output/<subfolder_nettoyé>."""
        node_dir = os.path.dirname(__file__)                   # .../ComfyUI/custom_nodes/Orion4D_MasterPrompt
        custom_nodes_dir = os.path.dirname(node_dir)           # .../ComfyUI/custom_nodes
        comfy_root = os.path.dirname(custom_nodes_dir)         # .../ComfyUI
        base_output = os.path.join(comfy_root, "output")       # .../ComfyUI/output
        safe_sub = _sanitize_subfolder(subfolder, "List_modified")
        return os.path.join(base_output, safe_sub)

    def run(
        self,
        text_in: str,
        find_replace_mode: str,
        find: str,
        replace: str,
        scope: str,
        ignore_case: bool,
        multiline: bool,
        dotall: bool,
        apply_per_line: bool,
        remove_blank_lines: bool,
        remove_duplicates: bool,
        sort_alpha: bool,
        descending: bool,
        case_insensitive: bool,
        remove_prefix_chars: int,
        remove_suffix_chars: int,
        add_prefix: str,
        add_suffix: str,
        save_output: bool,
        subfolder: str,
        file_basename: str,
        save_format: str,
    ):
        # 0) Find/Replace (avant tout)
        working_text = text_in
        if find_replace_mode != "none":
            if apply_per_line:
                lines = working_text.splitlines()
                new_lines = []
                for ln in lines:
                    new_ln, _ = self._apply_find_replace_text(
                        ln, find_replace_mode, find, replace, scope, ignore_case, multiline, dotall
                    )
                    new_lines.append(new_ln)
                working_text = "\n".join(new_lines)
            else:
                working_text, _ = self._apply_find_replace_text(
                    working_text, find_replace_mode, find, replace, scope, ignore_case, multiline, dotall
                )

        # 1) Split
        raw_lines = working_text.splitlines()

        # 2) Edit par ligne
        edited = [
            self._edit_line(ln, remove_prefix_chars, remove_suffix_chars, add_prefix, add_suffix)
            for ln in raw_lines
        ]

        # 3) Blanks
        if remove_blank_lines:
            edited = [ln for ln in edited if ln.strip() != ""]

        # 4) Dedupe
        if remove_duplicates:
            edited = self._dedupe_keep_order(edited)

        # 5) Sort
        if sort_alpha:
            if case_insensitive:
                edited.sort(key=lambda s: s.lower(), reverse=descending)
            else:
                edited.sort(reverse=descending)

        # 6) Join
        text_out = "\n".join(edited)

        # 7) Save
        saved_path = ""
        if save_output:
            try:
                out_dir = self._resolve_output_dir(subfolder)
                os.makedirs(out_dir, exist_ok=True)
                basename = _sanitize_basename(file_basename)
                ext = "csv" if save_format.lower() == "csv" else "txt"
                path = os.path.join(out_dir, f"{basename}.{ext}")
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(text_out)
                saved_path = os.path.abspath(path)
            except Exception as e:
                print(f"[MPListEditor] Save error: {e}")
                saved_path = ""

        return (text_out, saved_path)


NODE_CLASS_MAPPINGS = {"mp_list_editor": MPListEditor}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_list_editor": "MP • List Editor"}
