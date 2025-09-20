# Orion4D_MasterPrompt/list_selector_pro.py
import os
import csv
import server
from aiohttp import web

PromptServer = server.PromptServer

PKG_NAME = "Orion4D_MasterPrompt"
CATEGORY = "MasterPrompt"
BASE_DIR = os.path.join(os.path.dirname(__file__), "lists")  # sandbox

def _is_safe_rel_path(rel_path: str) -> bool:
    if rel_path is None:
        return False
    if rel_path in ("", "/"):  # racine autorisée
        return True
    if os.path.isabs(rel_path):
        return False
    norm = os.path.normpath(rel_path)
    if norm.startswith("..") or "/.." in norm or "\\.." in norm:
        return False
    return True

def _safe_join(rel_path: str) -> str:
    if rel_path in ("", "/"):
        return os.path.normpath(BASE_DIR)
    if not _is_safe_rel_path(rel_path):
        raise ValueError("Unsafe path")
    full = os.path.normpath(os.path.join(BASE_DIR, rel_path))
    base = os.path.normpath(BASE_DIR)
    if os.path.commonpath([full, base]) != base:
        raise ValueError("Path escapes sandbox")
    return full

def _read_lines(full_path: str):
    if not os.path.isfile(full_path):
        return []
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            if full_path.lower().endswith(".csv"):
                import csv as _csv
                reader = _csv.reader(f)
                return [", ".join(r).strip() for r in reader if any(field.strip() for field in r)]
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[{PKG_NAME}] read error {full_path}: {e}")
        return []

def _list_dirs_recursive(rel_dir: str):
    """Tous les sous-dossiers, récursif, chemins relatifs style 'demo/sub'."""
    root = _safe_join(rel_dir)
    res = []
    try:
        for cur, dirs, _files in os.walk(root):
            for d in dirs:
                p = os.path.join(cur, d)
                rel = os.path.relpath(p, BASE_DIR).replace("\\", "/")
                if rel == ".":
                    continue
                res.append(rel)
        res.sort()
    except Exception as e:
        print(f"[{PKG_NAME}] list_dirs error: {e}")
    return res

def _list_files(rel_dir: str):
    """Tous les .txt/.csv directement DANS ce dossier (non récursif)."""
    target = _safe_join(rel_dir)
    out = []
    try:
        for name in sorted(os.listdir(target)):
            if name.lower().endswith((".txt", ".csv")):
                rel = os.path.relpath(os.path.join(target, name), BASE_DIR).replace("\\", "/")
                out.append(rel)
    except Exception as e:
        print(f"[{PKG_NAME}] list_files error: {e}")
    return out

# ----------------------------- HTTP API -----------------------------

@PromptServer.instance.routes.get("/orion4d/mp/list_dirs")
async def http_list_dirs(request):
    rel = (request.rel_url.query.get("dir") or "").strip()
    if not _is_safe_rel_path(rel):
        return web.Response(status=400, text="Bad path")
    # renvoie racine '/' + tous les sous-dossiers récursifs
    return web.json_response(["/"] + _list_dirs_recursive(rel))

@PromptServer.instance.routes.get("/orion4d/mp/list_files")
async def http_list_files(request):
    rel = (request.rel_url.query.get("dir") or "").strip()
    if not _is_safe_rel_path(rel):
        return web.Response(status=400, text="Bad path")
    return web.json_response(_list_files(rel))

@PromptServer.instance.routes.post("/orion4d/mp/list_lines")
async def http_list_lines(request):
    data = await request.json()
    relfile = (data.get("file") or "").strip()
    if not _is_safe_rel_path(relfile):
        return web.Response(status=400, text="Bad path")
    full = _safe_join(relfile)
    return web.json_response(_read_lines(full))

# --------------------------------- Node ---------------------------------

class ListSelectorPro:
    """
    list_selector_pro
    - Menus déroulants (folder -> file -> selected_line) gérés côté JS
    - Navigation récursive sous ./lists + racine "/"
    - Mode 'select' (ligne choisie) ou 'random' (seedé côté frontend)
    - Pré/suffixes optionnels
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": ("STRING", {"default": "/", "multiline": False}),
                "file": ("STRING", {"default": "", "multiline": False}),
                "mode": (["select", "random"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "selected_line": ("STRING", {"default": ""}),
                "add_prefix": ("BOOLEAN", {"default": False}),
                "custom_prefix": ("STRING", {"default": "", "multiline": True}),
                "add_suffix": ("BOOLEAN", {"default": False}),
                "custom_suffix": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_text",)
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(self,
            folder, file, mode, seed,
            selected_line="",
            add_prefix=False, custom_prefix="",
            add_suffix=False, custom_suffix=""):

        relfile = (file or "").strip()
        if not relfile:
            return ("",)

        if not _is_safe_rel_path(relfile):
            return ("",)

        full = _safe_join(relfile)
        lines = _read_lines(full)
        if not lines:
            return ("",)

        if mode == "random":
            import random
            random.seed(seed)
            base = random.choice(lines)
        else:
            base = selected_line if selected_line in lines else lines[0]

        out = f"{custom_prefix if add_prefix else ''}{base}{custom_suffix if add_suffix else ''}"
        return (out,)

NODE_CLASS_MAPPINGS = {
    "list_selector_pro": ListSelectorPro
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "list_selector_pro": "MP • List Selector Pro"
}
