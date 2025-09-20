// Orion4D_MasterPrompt/web/orion4d_masterprompt.js
import { app } from "/scripts/app.js";

const API = {
  list_dirs: (dir = "/") =>
    fetch(`/orion4d/mp/list_dirs?dir=${encodeURIComponent(dir)}`).then(r => r.json()),
  list_files: (dir = "/") =>
    fetch(`/orion4d/mp/list_files?dir=${encodeURIComponent(dir)}`).then(r => r.json()),
  list_lines: (file) =>
    fetch(`/orion4d/mp/list_lines`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file })
    }).then(r => r.json()),
};

const ROOT = "/";

function replaceWithCombo(node, name, placeholder = "(select)") {
  // Trouve l’ancien widget
  const idx = node.widgets.findIndex(w => w.name === name);
  if (idx < 0) return null;
  const old = node.widgets[idx];

  // Supprime l’ancien widget
  node.widgets.splice(idx, 1);

  // Ajoute un combo au même index, même nom
  const combo = node.addWidget("combo", name, old.value ?? "", null, { values: [placeholder] });

  // Remettre le widget à la même position (addWidget l’ajoute en fin)
  const last = node.widgets.pop();
  node.widgets.splice(idx, 0, last);

  // Petite déco
  combo.label = name;
  node.graph?.setDirtyCanvas(true);
  return combo;
}

function setValues(widget, values, placeholder) {
  const vals = Array.isArray(values) && values.length ? values : [placeholder];
  widget.options ??= {};
  widget.options.values = vals;
  if (!vals.includes(widget.value)) widget.value = vals[0];
}

app.registerExtension({
  name: "Orion4D.MasterPrompt.ListSelectorPro",
  async nodeCreated(node) {
    if (node.constructor.type !== "list_selector_pro") return;

    console.debug("[MasterPrompt] init on node", node.id);

    // Remplace les trois widgets par de vrais combos
    const wFolder = replaceWithCombo(node, "folder", ROOT);
    const wFile   = replaceWithCombo(node, "file", "(no .txt/.csv here)");
    const wLine   = replaceWithCombo(node, "selected_line", "(pick a file)");

    const wMode = node.widgets.find(w => w.name === "mode");
    const wSeed = node.widgets.find(w => w.name === "seed");

    const pretty = (p) => (p === ROOT || p === "" ? " / (lists) " : p);

    const loadFolders = async () => {
      try {
        const dirs = await API.list_dirs(ROOT); // renvoie ["/", "demo", "demo/sub", ...]
        setValues(wFolder, dirs, ROOT);
        if (!wFolder.value) wFolder.value = ROOT;
        wFolder.label = `folder: ${pretty(wFolder.value)}`;
      } catch (e) {
        console.error("[MasterPrompt] loadFolders", e);
        setValues(wFolder, [ROOT], ROOT);
      }
      node.graph?.setDirtyCanvas(true);
    };

    const loadFiles = async () => {
      const dir = wFolder.value || ROOT;
      try {
        const files = await API.list_files(dir);
        setValues(wFile, files, "(no .txt/.csv here)");
      } catch (e) {
        console.error("[MasterPrompt] loadFiles", e);
        setValues(wFile, [], "(error)");
      }
      wFile.label = "file";
      node.graph?.setDirtyCanvas(true);
    };

    const loadLines = async () => {
      const file = wFile.value || "";
      if (!file || file.startsWith("(")) {
        setValues(wLine, [], "(pick a file)");
      } else {
        try {
          const lines = await API.list_lines(file);
          setValues(wLine, lines, "(empty file)");
        } catch (e) {
          console.error("[MasterPrompt] loadLines", e);
          setValues(wLine, [], "(error)");
        }
      }
      wLine.label = "selected_line";
      node.graph?.setDirtyCanvas(true);
    };

    // Chaînage dynamique
    wFolder.callback = async () => {
      await loadFiles();
      await loadLines();
      wFolder.label = `folder: ${pretty(wFolder.value)}`;
    };
    wFile.callback   = async () => { await loadLines(); };

    // Seed auto si random
    if (wMode && wSeed) {
      const orig = wMode.callback;
      wMode.callback = (...args) => {
        if (wMode.value === "random" && (!wSeed.value || wSeed.value === 0)) {
          wSeed.value = Math.floor(Math.random() * 2 ** 32);
        }
        orig?.apply(wMode, args);
      };
    }

    // Premier peuplement
    setTimeout(async () => { await loadFolders(); await loadFiles(); await loadLines(); }, 50);
  }
});
