# Orion4D_MasterPrompt/__init__.py

from .list_selector_pro import ListSelectorPro
from .multi_list_mixer import MultiListMixer
from .text_field_mixer import TextFieldMixer
from .mp_replace import MPReplace
from .mp_format import MPFormat
from .mp_wrap import MPWrap
from .mp_list_editor import MPListEditor
from .mp_file_txt_pro import MPFileTxtPro
from .mp_super_show_text import MPSuperShowText
from .text_prompt_mixer import TextPromptMixer
from .json_format_prompt import MPJsonFormat
from .json_merge import MPJsonMerge
from .json_pick import MPJsonPick
from .json_kv_lines import MPJsonKVLines
from .mp_folder_merge_lines import MPFolderMergeLines

NODE_CLASS_MAPPINGS = {
    "list_selector_pro": ListSelectorPro,
    "multi_list_mixer": MultiListMixer,
    "text_field_mixer": TextFieldMixer,
    "mp_replace": MPReplace,
    "mp_format": MPFormat,
    "mp_wrap": MPWrap,
    "mp_list_editor": MPListEditor,
    "mp_file_txt_pro": MPFileTxtPro,
    "mp_super_show_text": MPSuperShowText,
    "text_prompt_mixer": TextPromptMixer,
    "mp_json_format": MPJsonFormat,
    "mp_json_merge": MPJsonMerge,
    "mp_json_pick": MPJsonPick,
    "mp_json_kv_lines": MPJsonKVLines,
    "mp_folder_merge_lines": MPFolderMergeLines,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "list_selector_pro": "MP • List Selector Pro",
    "multi_list_mixer": "MP • Multi List Mixer",
    "text_field_mixer": "MP • Text Field Mixer",
    "mp_replace": "MP • Replace (Simple/Regex)",
    "mp_format": "MP • Format (Named/Indexed)",
    "mp_wrap": "MP • Wrap (Pairs/Custom)",
    "mp_list_editor": "MP • List Editor",
    "mp_file_txt_pro": "MP • File TXT (Pro)",
    "mp_super_show_text": "MP • Super Show Text",
    "text_prompt_mixer": "MP • Text Prompt Mixer",
    "mp_json_format": "MP • JSON Format (Prompt)",
    "mp_json_merge": "MP • JSON Merge (Deep)",
    "mp_json_pick": "MP • JSON Pick (Paths → Text)",
    "mp_json_kv_lines": "MP • JSON ↔︎ KV Lines",
    "mp_folder_merge_lines": "MP • Folder → Merge Lines",
}

# Sert les scripts front (JS) depuis ./web
WEB_DIRECTORY = "./web"
