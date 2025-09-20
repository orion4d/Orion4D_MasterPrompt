# Unified List Selector for ComfyUI

This project is a custom node for ComfyUI that allows you to dynamically load (no browser refresh required) lists from text or CSV files (specify the link in the field) and select an item to use in your workflow. It offers a manual selection mode (via a drop-down list) and a random selection mode, as well as the ability to add prefixes and suffixes to the selected text. Possibility of node chaining with suffix/prefix inputs and outputs.
---

## 🖼️ Preview

![image](https://github.com/user-attachments/assets/cf212622-5832-4242-be62-564c303b2ccb)


## ✨ Features

-   **Multiple File Loading**: Load lists from `.txt` files (one item per line) or `.csv` files (each row is treated as a single list entry, with columns joined by ", ").
-   **Interactive Dropdown Menu**: After providing a valid file path, a dropdown menu appears, populated with the file's content for easy selection.
-   **Dual Selection Mode**:
    -   `select`: Manually choose an item from the list.
    -   `random`: Let the node pick a random item (controlled by a seed for reproducibility).
-   **Text Customization**: Easily add custom prefixes and/or suffixes to the selected text.
-   **Dynamic Updates**: The dropdown list updates automatically when you change the file path.
-   **Error Handling**: Displays clear messages in the dropdown if the file is not found, empty, or the path is invalid.

## ⚙️ Installation

1.  Navigate to your ComfyUI `custom_nodes` directory.
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Clone this repository.
    ```bash
    git clone https://github.com/orion4d/ComfyUI_unified_list_selector.git
    ```

3.  Restart ComfyUI.

The node will be available under `Add Node > Custom/Tools > Unified List Selector`.

## 📖 How to Use

Once the node is added to your workflow, you can configure the following inputs:

### Node Inputs

-   **`list_file`** (STRING)
    -   **Description**: The absolute or relative path to your `.txt` or `.csv` file.
    -   **Examples**:
        -   Absolute path: `D:\ComfyUI\input\my_styles.txt`
        -   Relative path (from the `ComfyUI` folder): `input/my_prompts.csv`
-   **`mode`** (select | random)
    -   `select`: Enables manual selection mode. The item chosen in the `selected_line` dropdown will be used.
    -   `random`: Selects a random item from the file. The selection is based on the `seed` value.
-   **`seed`** (INT)
    -   **Description**: A seed for the random number generator. Only used when `mode` is set to `random`. Changing the seed will change the random item selected, but keeping the same seed ensures the same selection on every run.
-   **`add_prefix`** (BOOLEAN)
    -   **Description**: Check this box to prepend the text from `custom_prefix` to the selected item.
-   **`custom_prefix`** (STRING)
    -   **Description**: The text to add at the beginning. Will be ignored if `add_prefix` is disabled.
-   **`add_suffix`** (BOOLEAN)
    -   **Description**: Check this box to append the text from `custom_suffix` after the selected item.
-   **`custom_suffix`** (STRING)
    -   **Description**: The text to add at the end. Will be ignored if `add_suffix` is disabled.
-   **`selected_line`** (COMBO/Dropdown)
    -   **Description**: This dropdown menu appears once a valid file is loaded. It allows you to manually select a line. It is only used when `mode` is set to `select`.

### Node Output

-   **`selected_text`** (STRING)
    -   **Description**: The final string, including the selected (or random) item with any optional prefixes/suffixes. This output can be connected to any text input, such as a prompt.


<div align="center">

<h3>🌟 <strong>Show Your Support</strong></h3>

<p>If this project helped you, please consider giving it a ⭐ on GitHub!</p>

<p><strong>Made with ❤️ for the ComfyUI community</strong></p>

<p><strong>by Orion4D</strong></p>

<a href="https://ko-fi.com/orion4d">
<img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Buy Me A Coffee" height="41" width="174">
</a>

</div>
