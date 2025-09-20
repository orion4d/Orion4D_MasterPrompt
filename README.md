# Orion4D MasterPrompt Suite for ComfyUI

Welcome to the **MasterPrompt** suite, a collection of custom nodes for ComfyUI designed to supercharge your text, list, and JSON manipulation workflows. Whether you need to dynamically load styles from files, mix concepts with weighted probabilities, format complex prompts, or handle JSON data, this suite provides the necessary tools with intuitive and powerful user interfaces. As a bonus I have included a basic pack of thematic lists generated with gpt5, have fun!

![491900008-f19cc2e8-6faa-4e42-a4a8-d3d56299710a](https://github.com/user-attachments/assets/df3447e4-9e40-4a39-acaf-418b7ac4a48b)

<img width="2082" height="962" alt="image" src="https://github.com/user-attachments/assets/a2624a84-1723-49ef-965a-8e34ab25aa58" />
<img width="1479" height="1089" alt="image" src="https://github.com/user-attachments/assets/aa67956e-6f41-4f0f-9969-1fd3884d255f" />
<img width="1262" height="1147" alt="image" src="https://github.com/user-attachments/assets/95388d0b-1a1f-4483-98f3-413a1db3d518" />
<img width="797" height="1131" alt="image" src="https://github.com/user-attachments/assets/ffb581f6-ab57-4bbe-a4c1-a57e68ffe622" />
<img width="1116" height="1124" alt="image" src="https://github.com/user-attachments/assets/946c1eb9-7f27-4d4d-af93-1db55a208efe" />
<img width="1056" height="967" alt="image" src="https://github.com/user-attachments/assets/53e2b084-5f6f-4ebd-a989-18aa18f9ea3c" />
<img width="796" height="1169" alt="image" src="https://github.com/user-attachments/assets/d93cbc89-cc44-4cc2-9231-fd48c9bb2640" />

## ✨ Key Features

-   **Advanced File Management**: Navigate your folders, read `.txt` and `.csv` files, and merge them effortlessly.
-   **Dynamic User Interfaces**: Many nodes feature custom UIs that update in real-time without needing to refresh the browser.
-   **Weighted Mixing**: Control the selection probability of different text elements with an intuitive "temperature" system.
-   **Comprehensive Text Toolkit**: Replace, format, edit, and wrap text with precise options.
-   **JSON Powerhouse**: Merge, format, extract data, and convert JSON structures directly within your workflows.
-   **Seamless Integration**: Integrates perfectly with ComfyUI, with standard inputs/outputs for easy connection to other nodes.

## ⚙️ Installation

1.  Navigate to your ComfyUI `custom_nodes` directory.
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Clone this repository.
    ```bash
    git clone https://github.com/orion4d/Orion4D_MasterPrompt.git
    ```
3.  Restart ComfyUI.

The nodes will be available under the `Add Node > MasterPrompt` menu.

---

## 📖 Node Guide

Here is a detailed description of each node available in the MasterPrompt suite.

### 🗂️ Section 1: File and List Management

These nodes specialize in reading and manipulating text and CSV files.

#### 📂 MP • List Selector Pro
This node is a simple and efficient file explorer, sandboxed to the `ComfyUI/custom_nodes/Orion4D_MasterPrompt/lists` directory, for selecting a line from a file.

-   **Purpose**: To choose a specific or random line from predefined lists (`.txt` or `.csv`). Ideal for selecting styles, character names, or concepts.
-   **Key Features**:
    -   Recursive navigation through subdirectories.
    -   Two modes: `select` (manual choice) and `random` (random pick based on a `seed`).
    -   Easily add prefixes and suffixes.
    -   Dynamic updates for dropdown lists.
-   **Inputs**:
    -   `folder`: Dropdown menu to choose the folder.
    -   `file`: Dropdown menu to choose the file in the selected folder.
    -   `mode`: `select` or `random`.
    -   `seed`: Seed for the random mode.
    -   `selected_line`: Dropdown menu with the file's content for `select` mode.
    -   `custom_prefix` / `custom_suffix`: Text to add before/after.
-   **Output**:
    -   `selected_text`: The chosen line with any additions.

#### 🎛️ MP • Multi List Mixer
This node allows you to randomly select a line from *multiple* files, weighting the probability of choosing each file.

-   **Purpose**: To create varied prompts by drawing from different lists of concepts (e.g., a 70% chance to pick an art style, 30% a camera style).
-   **Key Features**:
    -   Dynamic interface to add/remove file sources.
    -   "Temperature" control (weight) for each file (0 to 10).
    -   The selection is a two-step process: 1) choose the file based on weights, 2) choose a random line from that file.
    -   Reproducible selection thanks to the `seed`.
-   **Inputs**:
    -   `config_json` (hidden): Automatically managed by the interface.
    -   `seed`: Seed for the random selection.
    -   `custom_prefix` / `custom_suffix`: Text to add.
-   **Output**:
    -   `mixed_text`: The single selected line.

#### 🗃️ MP • Folder → Merge Lines
Scans a folder (and its subfolders) to merge the content of all `.txt` and `.csv` files into one large list.

-   **Purpose**: To consolidate multiple files of keywords, styles, or negative prompts into a single text, ready to be used or saved.
-   **Key Features**:
    -   Recursive folder reading.
    -   Powerful cleaning options: remove duplicates, empty lines, etc.
    -   Advanced CSV support: select a specific column and handle headers.
    -   Option to save the result to a new file.
-   **Inputs**:
    -   `folder`: Path to the folder to analyze.
    -   `recursive`: Include subfolders.
    -   `csv_column`: Index of the column to extract from CSVs (-1 for the entire line).
    -   `deduplicate`, `skip_empty`...: Cleaning options.
    -   `save_output`, `save_folder`, `file_name`: To save the merged file.
-   **Outputs**:
    -   `merged_text`: The text containing all merged lines.
    -   `lines_count`: The total number of lines after processing.
    -   `saved_path`: The full path of the saved file.

#### 📜 MP • File TXT (Pro)
A complete and powerful file explorer to navigate your disk, filter files, and load the content of a `.txt` or `.csv` file.

-   **Purpose**: To provide a "file explorer" experience directly within ComfyUI for loading text, with search and sort tools.
-   **Key Features**:
    -   File browser-inspired interface.
    -   Folder navigation (up/down).
    -   Filter by regular expression (regex) on filenames.
    -   Sort by name or modification date.
    -   Preview on double-click, open in the system's file explorer.
-   **Inputs**:
    -   `directory`: The starting folder (can be changed via the UI).
    -   `name_regex`, `sort_by`... (hidden): Controlled by the graphical interface.
-   **Outputs**:
    -   `Txt`: The text content of the selected file.
    -   `file_path`: The absolute path of the selected file.

---
### ✍️ Section 2: Text Manipulation

These nodes are your Swiss army knife for transforming and cleaning strings.

#### 🔄 MP • Replace (Simple/Regex)
A simple yet powerful find-and-replace tool, with support for regular expressions (regex) and bulk replacements via JSON.

-   **Purpose**: To perform text substitutions, whether to fix errors, change keywords, or apply complex transformations.
-   **Key Features**:
    -   `simple` mode: Literal text replacement.
    -   `regex` mode: Uses regular expressions for advanced replacements.
    -   Scope control (`all` or `first` occurrence).
    -   Options for case sensitivity, `multiline`, and `dotall` for regex.
    -   `table_json` mode to apply a series of replacements at once.
-   **Inputs**:
    -   `text`: The source text.
    -   `find` / `replace`: The strings to search for and replace with.
    -   `table_json`: A JSON object like `{"word_to_find": "replacement", ...}`.
-   **Outputs**:
    -   `text_out`: The text after replacement.
    -   `replacements`: The number of substitutions made.

#### 📝 MP • List Editor
A complete pipeline to clean and restructure text lists (one item per line).

-   **Purpose**: To take a multiline text block, treat it as a list, and apply a series of cleaning, sorting, and modification operations.
-   **Key Features**:
    -   Find/replace at the beginning of the pipeline.
    -   Remove prefixes/suffixes by character count.
    -   Add prefixes/suffixes to each line.
    -   Cleaning: remove empty lines and duplicates.
    -   Alphabetical sorting (ascending/descending, case-sensitive or not).
    -   Optional saving of the result to a `.txt` or `.csv` file.
-   **Inputs**:
    -   `text_in`: The input list (separated by newlines).
    -   All processing options (find/replace, remove/add, sort, etc.).
-   **Outputs**:
    -   `text_out`: The final list, formatted as a single string.
    -   `saved_path`: The path of the saved file, if the option is enabled.

#### 🔗 MP • Format (Named/Indexed)
Formats a string using positional (`{0}`, `{1}`) and/or named (`{name}`) arguments.

-   **Purpose**: To dynamically build complex prompts by inserting text snippets into specific places in a template.
-   **Key Features**:
    -   Supports both placeholders like `{0}` and `{name}`.
    -   Up to 10 positional inputs (`arg_0` to `arg_9`).
    -   Named arguments can be provided via a JSON string or a Python dictionary.
    -   Policies for handling missing keys (`strict`, `skip-missing`, `default-empty`).
-   **Inputs**:
    -   `format_string`: The text template (e.g., `photo of a {0}, in the style of {artist}`).
    -   `arg_0`...`arg_9`: Inputs for positional placeholders.
    -   `kwargs_json`: A JSON string (`{"artist": "Van Gogh"}`) for named placeholders.
-   **Outputs**:
    -   `text_out`: The final formatted text.
    -   `diagnostic`: Information about the formatting process.

#### 🛀 MP • Wrap (Pairs/Custom)
Wraps text (or each line of a text) with predefined or custom character pairs.

-   **Purpose**: To quickly add parentheses, quotes, or any other delimiters to a text, useful for adjusting emphasis (weight) in a prompt.
-   **Key Features**:
    -   Numerous preset styles: `()`, `[]`, `{}`, `""`, `« »`, etc.
    -   `Custom` mode to define your own prefix and suffix.
    -   `per_line` option to apply wrapping to each line individually.
    -   Cleaning options (`trim_lines`, `skip_if_empty`).
-   **Inputs**:
    -   `text`: The text to wrap.
    -   `style`: The pair style to use.
    -   `per_line`: Apply to each line or the entire block.
-   **Output**:
    -   `wrapped_text`: The wrapped text.

#### 📺 MP • Super Show Text
An enhanced display node that shows a preview of the text, can number lines, and extract specific selections.

-   **Purpose**: To easily visualize and debug text content at any stage of a workflow, and to extract parts of a list for further processing.
-   **Key Features**:
    -   Text preview directly in the node.
    -   Can directly read a `.txt` or `.csv` file path.
    -   Optional line numbering with customizable prefixes/suffixes.
    -   Extract lines by number or range (e.g., `1-5`, `8`, `10-12`).
-   **Inputs**:
    -   `text`: The text to display (or a file path).
    -   `show_numbers`: Enables line numbering.
    -   `line_selector`: The line selection string.
-   **Outputs**:
    -   `text_out`: The full text (numbered if enabled).
    -   `selected_text`: Only the selected lines.

---
### 🎭 Section 3: Dynamic Mixers

These nodes combine multiple text inputs into a single output, either by assembly or by random selection.

#### 🎲 MP • Text Field Mixer
Combines several text fields by randomly choosing one, weighted by a "temperature". Similar to `Multi List Mixer`, but with internal text fields.

-   **Purpose**: To create variety by randomly choosing from a list of prompts or prompt fragments that you write directly in the node.
-   **Key Features**:
    -   Dynamic interface to add/remove up to 12 text fields.
    -   Each field has its own "temperature" (weight) from 0 to 10.
    -   Fields can be overridden by external inputs (`ext_text_1`...).
    -   If an external input is connected, the corresponding field is locked ("linked").
-   **Inputs**:
    -   `config_json` (hidden): Managed by the UI.
    -   `seed`: Seed for the random draw.
    -   `ext_text_1`...`ext_text_12` (optional): To connect text from other nodes.
-   **Output**:
    -   `mixed_text`: The single selected text field.

#### 🧩 MP • Text Prompt Mixer
Deterministically assembles multiple text fields using custom separators between each field.

-   **Purpose**: To build a final prompt by concatenating several parts (e.g., subject, action, style, composition) with full control over the separators.
-   **Key Features**:
    -   Dynamic interface to add/remove up to 12 fields.
    -   Each field has its own separator that will be inserted *after* it.
    -   Fields can be enabled/disabled or overridden by external inputs.
    -   Cleaning options (`trim`, `skip_empty`).
-   **Inputs**:
    -   `config_json` (hidden): Managed by the UI.
    -   `ext_text_1`...`ext_text_12` (optional): External inputs.
-   **Outputs**:
    -   `prompt_text`: The final assembled text.
    -   `parts_used`: The number of fields that were used.

---
### 📑 Section 4: JSON Toolkit

A suite of powerful nodes for manipulating structured data in JSON format.

#### 💅 MP • JSON Format (Prompt)
Takes a raw JSON string and pretty-prints, minifies, or escapes it for safe use in a prompt.

-   **Purpose**: To clean or prepare JSON data to be human-readable or interpretable by a language model (LLM).
-   **Key Features**:
    -   Tolerant parser (accepts Python dictionaries).
    -   Formatting options: `pretty` (indented), `sort_keys`, `compact_one_line`.
    -   Escaping options for prompts (`escape_newlines`, `escape_quotes`).
    -   Can wrap the result in a Markdown code block (```json...```).
-   **Input**:
    -   `json_in`: The JSON string or Python dictionary.
-   **Output**:
    -   `json_out`: The formatted JSON.

#### 🤝 MP • JSON Merge (Deep)
Deep merges 2 to 5 JSON objects into one.

-   **Purpose**: To combine multiple configurations or data structures. For example, merging a base JSON with a patch JSON.
-   **Key Features**:
    -   Recursive merging of dictionaries.
    -   Merge policies for arrays: `replace`, `concat`, `unique` (concatenate and remove duplicates).
    -   Option to remove keys with `null` values from the final result.
-   **Inputs**:
    -   `json_1`...`json_5`: The JSON strings to merge.
-   **Output**:
    -   `json_merged`: The resulting merged JSON object.

#### 👉 MP • JSON Pick (Paths → Text)
Extracts one or more values from a JSON object using access paths (e.g., `user.name`, `items[0].price`).

-   **Purpose**: To retrieve specific information from a complex data structure to use as text in a prompt.
-   **Key Features**:
    -   Simple and intuitive path syntax (`key.subkey[index]`).
    -   Extract multiple values at once (one path per line).
    -   Extracted values are joined with a customizable separator.
-   **Inputs**:
    -   `json_in`: The source JSON object.
    -   `paths`: The list of paths to extract, one per line.
    -   `joiner`: The separator to use between the found values.
-   **Outputs**:
    -   `picked_text`: The text containing the extracted values.
    -   `hits_count`: The number of paths that returned a value.

#### ↔️ MP • JSON ↔︎ KV Lines
Converts a JSON object into a list of `key: value` lines and vice versa.

-   **Purpose**: To facilitate editing of structured data in a simple text format or to convert `.ini`-style configuration files to JSON.
-   **Key Features**:
    -   **KV to JSON**: Parses `key: value` lines, supports nested paths (`a.b[0]: val`), comments, and type conversion (booleans, numbers).
    -   **JSON to KV**: Flattens a JSON structure into a list of `path: value` lines.
-   **Inputs/Options**:
    -   `mode`: `kv_to_json` or `json_to_kv`.
    -   Many options to customize separators, comment handling, etc.
-   **Output**:
    -   `text_out`: The result of the conversion.

## Dependencies

This node suite has been designed to be as easy to install as possible.

✅ **Zero external dependencies!**

You do not need to install any additional Python packages using `pip`. All functionalities rely either on Python's standard library or on components already included with ComfyUI. This means the installation is truly as simple as cloning the repository.

**Note: I am not a volunteer for training and to carry out professional workflows with these nodes.
---

<div align="center">

<h3>🌟 <strong>Show Your Support</strong></h3>

<p>If this project helped you, please consider giving it a ⭐ on GitHub!</p>

<p><strong>Made with ❤️ for the ComfyUI community</strong></p>

<p><strong>by Orion4D</strong></p>

<a href="https://ko-fi.com/orion4d">
<img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Buy Me A Coffee" height="41" width="174">
</a>

</div>
