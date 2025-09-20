// custom_nodes/Orion4D_MasterPrompt/web/mp_super_show_text.js
"use strict";
import { app } from "/scripts/app.js";

function getTextFromExecutedArgs(args) {
  // Tolérant: on cherche un objet qui contient ui.text, text, result[0]... dans TOUS les arguments
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (!a || typeof a !== "object") continue;

    // cas classique: msg.ui.text (ce que renvoie ton .py)
    if (a.ui && a.ui.text != null) {
      const t = a.ui.text;
      return Array.isArray(t) ? t.join("") : String(t);
    }
    // fallback: msg.text
    if (a.text != null) {
      const t = a.text;
      return Array.isArray(t) ? t.join("") : String(t);
    }
    // autre fallback: result[0]
    if (Array.isArray(a.result) && a.result.length) {
      return String(a.result[0] ?? "");
    }
    // certains fronts emballent encore une couche
    if (a.output && a.output.ui && a.output.ui.text != null) {
      const t = a.output.ui.text;
      return Array.isArray(t) ? t.join("") : String(t);
    }
  }
  return "";
}

app.registerExtension({
  name: "Orion4D.MPSuperShowText.WrapAndAutosize.Fixed",

  nodeCreated(node) {
    if (node.constructor.type !== "mp_super_show_text") return;

    // ---------- UI preview
    const root = document.createElement("div");
    root.style = "display:flex;flex-direction:column;gap:6px;width:100%;";

    const label = document.createElement("div");
    label.textContent = "Aperçu — texte complet";
    label.style = "opacity:.85;font-size:12px;padding:2px 0;";

    const view = document.createElement("div");
    view.textContent = "— (vide) —";
    view.style = [
      "border:1px solid #2f2f2f",
      "border-radius:8px",
      "padding:8px",
      "min-height:100px",
      "max-height:420px",
      "overflow:auto",
      "font-family:ui-monospace,Menlo,Consolas,monospace",
      "font-size:13px",
      "line-height:1.35",
      "background:#111",
      "color:#e0e0e0",
      "white-space:pre-wrap",     // wrap auto (garde les \n)
      "overflow-wrap:anywhere",   // casse les très longues chaînes
      "word-break:break-word"
    ].join(";");

    root.append(label, view);
    node.addDOMWidget("mp_super_show_text_preview", "div", root, {});

    // ---------- autosize
    const ensureMinNodeHeight = () => {
      if (!node.size) node.size = [520, 360];
      node.size[1] = Math.max(node.size[1], 360); // un minimum pour éviter l’écrasement
    };
    const resize = () => {
      // réserve approximativement la place des widgets au-dessus
      const topReserve = 185; // ajuste si tu ajoutes des champs
      const free = Math.max(120, node.size[1] - topReserve);
      view.style.maxHeight = free + "px";
      view.style.minHeight = Math.min(160, free) + "px";
    };
    ensureMinNodeHeight();
    resize();

    const oldResize = node.onResize;
    node.onResize = function (w, h) {
      ensureMinNodeHeight();
      resize();
      return oldResize ? oldResize.call(this, w, h) : [w, h];
    };

    // ---------- alimentation du preview après exécution
    const oldExec = node.onExecuted;
    node.onExecuted = function () {
      try {
        const text = getTextFromExecutedArgs(arguments);
        view.textContent = text && text.length ? text : "— (vide) —";
      } catch {
        view.textContent = "(erreur d’aperçu)";
      }
      resize();
      if (oldExec) return oldExec.apply(this, arguments);
    };
  },
});

console.log("[Orion4D] MP • Super Show Text — preview fixé (wrap + autosize)");
