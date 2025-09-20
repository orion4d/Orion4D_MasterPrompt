# Orion4D_MasterPrompt/mp_folder_merge_lines.py
# MP • Folder → Merge Lines
# - Parcourt un dossier (option récursif)
# - Charge .txt et .csv (tri alphabétique, insensible à la casse)
# - Fusionne ligne par ligne pour produire une liste (STRING)
# - Options: trim, skip_empty, deduplicate, collapse_blank_lines, max_lines
# - CSV: choisir une colonne, délimiteur, ignorer l’entête
# - Sauvegarde optionnelle du texte fusionné

import os, csv
from typing import List, Tuple

CATEGORY = "MasterPrompt"

def _norm_folder(path: str) -> str:
    p = (path or "").strip()
    if not p:
        return ""
    return os.path.abspath(os.path.expanduser(p))

def _iter_files(folder: str, recursive: bool, exts: Tuple[str, ...]) -> List[str]:
    files: List[str] = []
    if recursive:
        for root, _, fnames in os.walk(folder):
            for f in fnames:
                if os.path.splitext(f)[1].lower() in exts:
                    files.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder):
            p = os.path.join(folder, f)
            if os.path.isfile(p) and os.path.splitext(f)[1].lower() in exts:
                files.append(p)
    # tri alphabétique insensible à la casse
    files.sort(key=lambda s: os.path.basename(s).casefold())
    return files

def _collapse_blank_lines(lines: List[str]) -> List[str]:
    out, prev_blank = [], False
    for ln in lines:
        blank = (ln.strip() == "")
        if blank and prev_blank:
            continue
        out.append(ln)
        prev_blank = blank
    return out

class MPFolderMergeLines:
    """
    Inputs:
      - folder: chemin du dossier à lire (relatif ou absolu)
      - recursive: inclure les sous-dossiers
      - include_csv: activer la lecture CSV
      - csv_column: -1 = ligne entière, sinon index de colonne à extraire
      - csv_delimiter: séparateur CSV ("," ";" "|", etc.)
      - csv_skip_header: ignorer la 1ère ligne CSV
      - trim_each / skip_empty / deduplicate / collapse_blank_lines
      - max_lines: 0 = illimité
      - save_output: écrire un fichier
      - save_folder + file_name: destination du fichier
    Outputs:
      - merged_text: liste finale (STRING)
      - files_used: noms de fichiers utilisés (STRING, lignes)
      - lines_count: nombre de lignes après traitements
      - saved_path: chemin du fichier écrit (ou vide)
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": ("STRING", {"default": "lists", "multiline": False}),
                "recursive": ("BOOLEAN", {"default": False}),
                "include_csv": ("BOOLEAN", {"default": True}),
                "csv_column": ("INT", {"default": -1, "min": -1, "max": 4096}),
                "csv_delimiter": ("STRING", {"default": ","}),
                "csv_skip_header": ("BOOLEAN", {"default": False}),
                "trim_each": ("BOOLEAN", {"default": True}),
                "skip_empty": ("BOOLEAN", {"default": True}),
                "deduplicate": ("BOOLEAN", {"default": False}),
                "collapse_blank_lines": ("BOOLEAN", {"default": False}),
                "max_lines": ("INT", {"default": 0, "min": 0, "max": 1_000_000}),
                "save_output": ("BOOLEAN", {"default": False}),
                "save_folder": ("STRING", {"default": "output/lists"}),
                "file_name": ("STRING", {"default": "merged_list.txt"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("merged_text", "files_used", "lines_count", "saved_path")
    FUNCTION = "run"
    CATEGORY = CATEGORY

    def run(
        self,
        folder: str,
        recursive: bool,
        include_csv: bool,
        csv_column: int,
        csv_delimiter: str,
        csv_skip_header: bool,
        trim_each: bool,
        skip_empty: bool,
        deduplicate: bool,
        collapse_blank_lines: bool,
        max_lines: int,
        save_output: bool,
        save_folder: str,
        file_name: str,
    ):
        root = _norm_folder(folder)
        if not root or not os.path.isdir(root):
            return ("", "", 0, "")

        exts = (".txt", ".csv") if include_csv else (".txt",)
        files = _iter_files(root, recursive, exts)

        lines: List[str] = []
        seen = set()

        for fp in files:
            ext = os.path.splitext(fp)[1].lower()
            try:
                if ext == ".txt":
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        for ln in f.read().splitlines():
                            s = ln.strip() if trim_each else ln
                            if skip_empty and s == "":
                                continue
                            if deduplicate:
                                if s in seen:
                                    continue
                                seen.add(s)
                            lines.append(s)
                elif ext == ".csv":
                    with open(fp, "r", encoding="utf-8", errors="ignore", newline="") as f:
                        reader = csv.reader(f, delimiter=(csv_delimiter or ","))
                        first = True
                        for row in reader:
                            if first and csv_skip_header:
                                first = False
                                continue
                            first = False
                            if csv_column >= 0:
                                if csv_column < len(row):
                                    cell = row[csv_column]
                                else:
                                    continue
                                s = cell.strip() if trim_each else cell
                            else:
                                # ligne CSV complète jointe par le délimiteur demandé (sans espaces)
                                s = (csv_delimiter or ",").join(row)
                                if trim_each:
                                    s = s.strip()
                            if skip_empty and s == "":
                                continue
                            if deduplicate:
                                if s in seen:
                                    continue
                                seen.add(s)
                            lines.append(s)
            except Exception:
                # on ignore le fichier problématique pour rester robuste
                continue

            if max_lines and len(lines) >= max_lines:
                lines = lines[:max_lines]
                break

        if collapse_blank_lines:
            lines = _collapse_blank_lines(lines)

        merged_text = "\n".join(lines)
        files_used = "\n".join([os.path.basename(p) for p in files])
        saved_path = ""

        if save_output:
            out_dir = _norm_folder(save_folder)
            try:
                os.makedirs(out_dir, exist_ok=True)
                out_name = file_name.strip() or "merged_list.txt"
                out_path = os.path.join(out_dir, out_name)
                with open(out_path, "w", encoding="utf-8", errors="ignore", newline="\n") as f:
                    f.write(merged_text)
                saved_path = out_path
            except Exception:
                saved_path = ""

        return (merged_text, files_used, len(lines), saved_path)


NODE_CLASS_MAPPINGS = {"mp_folder_merge_lines": MPFolderMergeLines}
NODE_DISPLAY_NAME_MAPPINGS = {"mp_folder_merge_lines": "MP • Folder → Merge Lines"}
