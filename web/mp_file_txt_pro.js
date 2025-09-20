// custom_nodes/Orion4D_MasterPrompt/web/mp_file_txt_pro.js
"use strict";

import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

let FOLDER_ICO = null;
try { FOLDER_ICO = new URL("./ico_dossier.png", import.meta.url).href; } catch {}
const FOLDER_SVG = `
<svg viewBox="0 0 24 24" width="24" height="18" fill="#f6c945" stroke="#b88a0a" stroke-width="1.1">
  <path d="M3 6h6l2 2h10a1 1 0 0 1 1 1v8.5a1.5 1.5 0 0 1-1.5 1.5H4.5A1.5 1.5 0 0 1 3 17.5V6z"/>
</svg>`;

function matchesNode(nd){ if(!nd) return false;
  const n=(nd.name||"").toLowerCase(), t=(nd.title||"").toLowerCase();
  return n==="mp_file_txt_pro" || t.includes("file txt");
}

app.registerExtension({
  name: "Orion4D.MPFileTxtPro.UI.FFPStyle",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (!matchesNode(nodeData)) return;

    const orig = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      if (orig) orig.apply(this, arguments);

      // widgets Comfy
      const wDir   = this.widgets?.find(w=>w.name==="directory");
      const wState = this.widgets?.find(w=>w.name==="state_json");
      const wRegex = this.widgets?.find(w=>w.name==="name_regex");
      const wMode  = this.widgets?.find(w=>w.name==="regex_mode");
      const wIg    = this.widgets?.find(w=>w.name==="regex_ignore_case");
      const wSort  = this.widgets?.find(w=>w.name==="sort_by");
      const wDesc  = this.widgets?.find(w=>w.name==="descending");

      // cacher + “collapser” les widgets techniques
      [wState,wRegex,wMode,wIg,wSort,wDesc].forEach(w=>{
        if(!w) return; w.hidden = true; w.computeSize = () => [0, -6];
      });
      // retirer les pastilles d’entrée parasites
      const kill = new Set(["state_json","name_regex","regex_mode","regex_ignore_case","sort_by","descending"]);
      if (Array.isArray(this.inputs)) this.inputs = this.inputs.filter(i => !kill.has(i?.name));

      // === UI (proche de Folder File Pro) ===
      const root = document.createElement("div");
      root.innerHTML = `
<style>
  .mft-root{height:100%;width:100%;box-sizing:border-box;display:flex;flex-direction:column;
            padding:6px;color:#ddd;font-family:Inter,Arial,Helvetica,sans-serif}
  .mft-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 6px 0}
  .mft-input,.mft-btn,.mft-sel{background:#333;color:#ccc;border:1px solid #555;border-radius:6px;padding:6px 8px;font-size:12px}
  .mft-input{flex:1 1 auto;min-width:260px}
  details.mft-opt{margin:0 0 6px 0}
  details.mft-opt summary{cursor:pointer;opacity:.9}
  .mft-opt-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
  .mft-list{flex:1 1 auto;min-height:180px;max-height:520px;overflow:auto;background:#1f1f1f;border-radius:10px;padding:6px}
  .mft-rowItem{display:flex;align-items:center;gap:10px;padding:6px 8px;border-radius:8px;user-select:none;cursor:pointer}
  .mft-rowItem:hover{background:#2a2a2a}
  .mft-rowItem.selected{outline:2px solid #00ffc9}
  .mft-ico{width:24px;height:18px;display:flex;align-items:center;justify-content:center}
  .mft-name{font-size:12px;word-break:break-all}
  .mft-ext{display:flex;align-items:center;justify-content:center;border:1px solid #777;border-radius:6px;width:46px;height:20px;font-size:10px;background:#262626}
  .mft-count{margin-left:auto;opacity:.85;font-size:12px}
</style>
<div class="mft-root">
  <!-- Ligne 1 -->
  <div class="mft-row">
    <button class="mft-btn mft-up">Up</button>
    <input class="mft-input mft-path" placeholder="Chemin dossier…"/>
    <button class="mft-btn mft-refresh">Refresh</button>
    <button class="mft-btn mft-explore">Explorer</button>
    <div class="mft-count"></div>
  </div>

  <!-- Onglet Options (recherche/tri) -->
  <details class="mft-opt">
    <summary>Options</summary>
    <div class="mft-opt-grid">
      <input class="mft-input opt-regex" placeholder="name_regex (ex: ^bo)">
      <select class="mft-sel opt-mode">
        <option value="off">regex: off</option>
        <option value="include">include</option>
        <option value="exclude">exclude</option>
      </select>
      <label><input type="checkbox" class="opt-ic"> ignore_case</label>
      <select class="mft-sel opt-sort">
        <option value="name">sort: name</option>
        <option value="mtime">sort: mtime</option>
      </select>
      <label><input type="checkbox" class="opt-desc"> descending</label>
    </div>
  </details>

  <!-- Liste -->
  <div class="mft-list" tabindex="0">
    <div style="padding:8px;opacity:.8">Choisis un dossier, puis Refresh.</div>
  </div>
</div>`;

      this.addDOMWidget("mp_file_txt_pro", "div", root, {});
      this.size = [850, 600]; // marge confortable : plus de chevauchement

      // refs
      const listEl = root.querySelector(".mft-list");
      const upBtn = root.querySelector(".mft-up");
      const pathInput = root.querySelector(".mft-path");
      const goBtn = root.querySelector(".mft-refresh");
      const exploreBtn = root.querySelector(".mft-explore");
      const countLbl = root.querySelector(".mft-count");

      const iRegex = root.querySelector(".opt-regex");
      const sMode  = root.querySelector(".opt-mode");
      const cbIg   = root.querySelector(".opt-ic");
      const sSort  = root.querySelector(".opt-sort");
      const cbDesc = root.querySelector(".opt-desc");

      // init depuis widgets cachés
      iRegex.value = wRegex?.value ?? "";
      sMode.value  = wMode?.value ?? "off";
      cbIg.checked = !!(wIg?.value ?? true);
      sSort.value  = wSort?.value ?? "name";
      cbDesc.checked = !!(wDesc?.value ?? false);

      // état
      let parentDir = null, isLoading = false;
      let currentFiles = []; let typeBuffer = ""; let typeTimer = null;

      const folderIcoHTML = () => FOLDER_ICO
        ? `<img class="mft-ico" src="${FOLDER_ICO}" alt="folder">`
        : `<div class="mft-ico">${FOLDER_SVG}</div>`;

      const rowHTML = (e,isDir)=>{
        if(isDir) return `<div class="mft-rowItem" data-type="dir" data-path="${e.path}">
          ${folderIcoHTML()}<div class="mft-name" title="${e.name}">${e.name}</div></div>`;
        const ext=(e.ext||"").toUpperCase()||".TXT";
        return `<div class="mft-rowItem" data-type="file" data-path="${e.path}">
          <div class="mft-ext">${ext}</div><div class="mft-name" title="${e.name}">${e.name}</div></div>`;
      };

      const setState = (patch)=>{
        if(!wState) return;
        let obj={}; try{ obj=JSON.parse(wState.value||"{}"); }catch{}
        Object.assign(obj, patch||{});
        wState.value = JSON.stringify(obj);
        this.setDirtyCanvas(true,true);
      };

      // récupération (filtre/tri côté serveur)
      const fetchList = async ()=>{
        if(isLoading) return; isLoading=true;
        const params = new URLSearchParams({
          directory: String(wDir?.value ?? ""),
          name_regex: iRegex.value,
          regex_mode: sMode.value,
          regex_ignore_case: String(cbIg.checked),
          sort_by: sSort.value,
          descending: String(cbDesc.checked),
        }).toString();
        listEl.style.opacity="0.65"; listEl.innerHTML="";
        try{
          // sync -> widgets cachés
          if (wRegex) wRegex.value = iRegex.value;
          if (wMode)  wMode.value  = sMode.value;
          if (wIg)    wIg.value    = cbIg.checked;
          if (wSort)  wSort.value  = sSort.value;
          if (wDesc)  wDesc.value  = cbDesc.checked;

          const res=await api.fetchApi("/mp_file_txt_pro/list?"+params);
          if(!res.ok) throw new Error("HTTP "+res.status);
          const data=await res.json();

          pathInput.value = data.current_directory || "";
          parentDir = data.parent_directory || null;
          upBtn.disabled = !parentDir;

          const dirs=data.dirs||[], files=data.files||[];
          currentFiles = files;
          countLbl.textContent = `${files.length} fichier(s)`;

          const frag=document.createDocumentFragment();
          for(const d of dirs){ const div=document.createElement("div"); div.innerHTML=rowHTML(d,true); frag.appendChild(div.firstElementChild); }
          for(const f of files){ const div=document.createElement("div"); div.innerHTML=rowHTML(f,false); frag.appendChild(div.firstElementChild); }
          listEl.appendChild(frag);
          listEl.focus();
        }catch(e){
          listEl.innerHTML=`<div style="padding:8px;color:#ff8888">${e.message||e}</div>`;
        }finally{
          isLoading=false; listEl.style.opacity="1";
        }
      };

      // interactions (comme Folder File Pro)
      listEl.addEventListener("click",(e)=>{
        const row=e.target.closest(".mft-rowItem"); if(!row) return;
        listEl.querySelectorAll(".mft-rowItem").forEach(r=>r.classList.remove("selected"));
        row.classList.add("selected");
        if(row.dataset.type==="file") setState({selected_path: row.dataset.path||""});
      });

      listEl.addEventListener("dblclick",(e)=>{
        const row=e.target.closest(".mft-rowItem"); if(!row) return;
        const p=row.dataset.path||"";
        if(row.dataset.type==="dir"){ if(wDir){ wDir.value=p; fetchList(); } return; }
        window.open("/mp_file_txt_pro/view?filepath="+encodeURIComponent(p), "_blank");
      });

      // tape-pour-sélectionner (côté fichiers)
      listEl.addEventListener("keydown",(e)=>{
        if (e.metaKey || e.ctrlKey || e.altKey) return;
        const ch = e.key.length===1 ? e.key : "";
        if (!ch) return;
        e.preventDefault();
        const now=Date.now();
        if (typeTimer && now-typeTimer<800) typeBuffer+=ch; else typeBuffer=ch;
        typeTimer=now;
        const want=typeBuffer.toLowerCase();
        const hit=currentFiles.find(f=>(f.name||"").toLowerCase().startsWith(want));
        if(hit){
          const row=listEl.querySelector(`.mft-rowItem[data-path="${CSS.escape(hit.path)}"]`);
          if(row){ row.scrollIntoView({block:"nearest"}); row.click(); }
        }
      });

      // barre
      const goUp = ()=>{ if(parentDir && wDir){ wDir.value=parentDir; fetchList(); } };
      upBtn.onclick = goUp;
      goBtn.onclick = ()=>{ if(wDir){ wDir.value = pathInput.value; fetchList(); } };
      exploreBtn.onclick = async ()=>{
        let p=""; try{ p=JSON.parse(wState?.value||"{}").selected_path || ""; }catch{}
        if(!p) p = String(wDir?.value || "");
        if(!p) return;
        try{
          await api.fetchApi("/mp_file_txt_pro/open_explorer",{
            method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({path:p})
          });
        }catch{}
      };

      // auto refresh
      [iRegex,sMode,cbIg,sSort,cbDesc].forEach(el=>{
        el?.addEventListener("change", fetchList);
        el?.addEventListener("input",  fetchList);
      });
      if (wDir) {
        const prev = wDir.callback;
        wDir.callback = function(){ prev && prev.apply(wDir, arguments); fetchList(); };
      }

      // init
      (async ()=>{
        try{
          const r=await api.fetchApi("/mp_file_txt_pro/get_last_path");
          const d=await r.json();
          const last = d.last_path || (wDir?.value || "");
          if(last && wDir) wDir.value = last;
          pathInput.value = last || "";
        }catch{}
        fetchList();
      })();
    };
  },
});

console.log("[Orion4D] MP • File TXT (Pro) UI (FFP-style) chargé");
