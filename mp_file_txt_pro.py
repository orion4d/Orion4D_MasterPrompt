# Orion4D_MasterPrompt/mp_file_txt_pro.py
# MP • File TXT (Pro) — Browser TXT/CSV ultra simple, filtre/tri côté serveur.
import os, io, json, re
from typing import List, Tuple

try:
    from server import PromptServer
    from aiohttp import web
except Exception:
    PromptServer = None
    web = None

CATEGORY = "MasterPrompt"
TXT_EXTS = {".txt", ".csv"}
_LAST_PATH = {"dir": ""}


def _is_txt(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in TXT_EXTS


def _abs(path: str) -> str:
    try:
        return os.path.abspath(path)
    except Exception:
        return path


def _list_dir(directory: str) -> Tuple[str, List[dict], List[dict]]:
    cur = _abs(directory or os.getcwd())
    dirs, files = [], []
    try:
        for name in os.listdir(cur):
            p = os.path.join(cur, name)
            if os.path.isdir(p):
                dirs.append({"name": name, "path": _abs(p)})
            elif os.path.isfile(p) and _is_txt(p):
                st = None
                try: st = os.stat(p)
                except Exception: pass
                files.append({
                    "name": name,
                    "path": _abs(p),
                    "ext": os.path.splitext(name)[1].lower(),
                    "mtime": int(st.st_mtime) if st else 0,
                })
    except Exception:
        pass
    dirs.sort(key=lambda d: d["name"].lower())
    files.sort(key=lambda f: f["name"].lower())
    return cur, dirs, files


def _read_text(path: str) -> str:
    if not path or not os.path.isfile(path) or not _is_txt(path):
        return ""
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        try:
            with open(path, "rb") as f:
                return f.read().decode("utf-8", errors="replace")
        except Exception:
            return ""


def _filter_files(files: List[dict], pattern: str, mode: str, ignore_case: bool) -> List[dict]:
    if not pattern or mode == "off":
        return files
    flags = re.IGNORECASE if ignore_case else 0
    try:
        rx = re.compile(pattern, flags)
    except Exception:
        return files
    if mode == "include":
        return [f for f in files if rx.search(f["name"])]
    else:  # exclude
        return [f for f in files if not rx.search(f["name"])]


def _sort_files(files: List[dict], key: str, desc: bool) -> List[dict]:
    if key == "mtime":
        return sorted(files, key=lambda f: f.get("mtime", 0), reverse=desc)
    return sorted(files, key=lambda f: f["name"].lower(), reverse=desc)


# ------------------------- Routes HTTP -------------------------
def _register_routes():
    if PromptServer is None or web is None:
        return
    routes = PromptServer.instance.routes

    @routes.get("/mp_file_txt_pro/list")
    async def list_handler(request):
        directory = request.query.get("directory", "") or _LAST_PATH.get("dir", "")
        name_regex = request.query.get("name_regex", "")
        regex_mode = request.query.get("regex_mode", "off")
        regex_ignore_case = request.query.get("regex_ignore_case", "true").lower() == "true"
        sort_by = request.query.get("sort_by", "name")
        descending = request.query.get("descending", "false").lower() == "true"

        cur, dirs, files = _list_dir(directory)
        files = _filter_files(files, name_regex, regex_mode, regex_ignore_case)
        files = _sort_files(files, sort_by, descending)

        _LAST_PATH["dir"] = cur
        parent = _abs(os.path.dirname(cur)) if os.path.dirname(cur) and os.path.isdir(os.path.dirname(cur)) else None
        return web.json_response({
            "current_directory": cur,
            "parent_directory": parent,
            "dirs": dirs,
            "files": files,
            "total_count": len(dirs) + len(files),
        })

    @routes.get("/mp_file_txt_pro/get_last_path")
    async def last_path_handler(request):
        return web.json_response({"last_path": _LAST_PATH.get("dir", "")})

    @routes.get("/mp_file_txt_pro/view")
    async def view_handler(request):
        filepath = request.query.get("filepath", "")
        if not filepath or not os.path.isfile(filepath) or not _is_txt(filepath):
            return web.Response(text="File not found or not allowed.", status=404)
        return web.Response(text=_read_text(filepath), content_type="text/plain", charset="utf-8")

    @routes.post("/mp_file_txt_pro/open_explorer")
    async def open_explorer(request):
        try:
            body = await request.json()
            path = body.get("path", "")
            if not path: return web.json_response({"ok": False})
            open_path = path if os.path.isdir(path) else os.path.dirname(path)
            if os.name == "nt":
                os.startfile(open_path)  # type: ignore
            elif hasattr(os, "uname") and os.uname().sysname.lower() == "darwin":  # type: ignore
                import subprocess; subprocess.Popen(["open", open_path])
            else:
                import subprocess; subprocess.Popen(["xdg-open", open_path])
            return web.json_response({"ok": True})
        except Exception:
            return web.json_response({"ok": False})

_register_routes()


# --------------------------- Node ---------------------------
class MPFileTxtPro:
    """
    Entrées visibles :
      - directory
    Caché (piloté par l'UI) :
      - state_json  => {"selected_path": "..."}
      - name_regex / regex_mode / regex_ignore_case / sort_by / descending
    Sorties :
      - Txt (contenu)
      - file_path (chemin)
    """
    OUTPUT_NODE = True   # autorise l’exécution sans rien brancher en sortie

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": "", "multiline": False}),
                "state_json": ("STRING", {"default": "{}", "multiline": True}),  # caché
                "name_regex": ("STRING", {"default": ""}),
                "regex_mode": (["off", "include", "exclude"],),
                "regex_ignore_case": ("BOOLEAN", {"default": True}),
                "sort_by": (["name", "mtime"],),
                "descending": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Txt", "file_path")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(
        self,
        directory: str,
        state_json: str,
        name_regex: str,
        regex_mode: str,
        regex_ignore_case: bool,
        sort_by: str,
        descending: bool,
    ):
        cur, _, files_all = _list_dir(directory)
        files = _filter_files(files_all, name_regex, regex_mode, regex_ignore_case)
        files = _sort_files(files, sort_by, descending)

        sel_path = ""
        try:
            data = json.loads(state_json or "{}")
            sel_path = str(data.get("selected_path", "")).strip()
        except Exception:
            sel_path = ""

        # pas de sélection → on prend le premier fichier filtré/trié
        if not sel_path and files:
            sel_path = files[0]["path"]

        txt = _read_text(sel_path) if sel_path else ""
        return (txt, _abs(sel_path) if sel_path else "")


NODE_CLASS_MAPPINGS = {"mp_file_txt_pro": MPFileTxtPro}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_file_txt_pro": "MP • File TXT (Pro)"}
