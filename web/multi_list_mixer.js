// Orion4D_MasterPrompt/web/multi_list_mixer.js
// Multi List Mixer UI: boutons +/− en haut (avant seed), lignes dynamiques,
// prefix/suffix tout en bas, config_json totalement masqué.

import { app } from "/scripts/app.js";

const ROOT = "/";

function debounce(fn, wait = 80){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),wait); }; }
async function safeJSON(r){ try{ return await r.json(); } catch{ return []; } }

const API = {
  list_dirs: async (dir=ROOT)=> safeJSON(await fetch(`/orion4d/mp/list_dirs?dir=${encodeURIComponent(dir)}`)),
  list_files: async (dir=ROOT)=> safeJSON(await fetch(`/orion4d/mp/list_files?dir=${encodeURIComponent(dir)}`)),
};

const findW = (node,name)=> node.widgets?.find(w=>w.name===name);
const wIndex = (node,w)=> node.widgets.indexOf(w);
const prettyFolder = (p)=>(p===ROOT||p==="")?" / (lists) ":p;

function setComboValues(w,vals,fallback){
  const v = Array.isArray(vals)&&vals.length? vals : [fallback];
  w.options ??= {}; w.options.values = v;
  if (!v.includes(w.value)) w.value = v[0];
}

function readRows(node){
  const rows=[];
  for(let i=0;;i++){
    const wf=findW(node,`folder_${i}`), wfile=findW(node,`file_${i}`), wt=findW(node,`temperature_${i}`);
    if(!wf||!wfile||!wt) break;
    rows.push({ folder: wf.value||ROOT, file: wfile.value||"", temperature: Number(wt.value)||0 });
  }
  return rows;
}

const saveConfig = debounce((node)=>{
  const wCfg = findW(node,"config_json"); if(!wCfg) return;
  const cleaned = readRows(node)
    .filter(r=>r.file && !String(r.file).startsWith("("))
    .map(r=>({ folder:r.folder, file:r.file, temperature: Math.max(0,Math.min(10, Number(r.temperature)||0)) }));
  wCfg.value = JSON.stringify(cleaned, null, 2);
  node.graph?.setDirtyCanvas(true);
}, 40);

// ---------- Bloc bas: prefix/suffix + config_json ----------
function getBottomBlock(node){
  return {
    ap:  findW(node,"add_prefix"),
    cp:  findW(node,"custom_prefix"),
    as:  findW(node,"add_suffix"),
    cs:  findW(node,"custom_suffix"),
    cfg: findW(node,"config_json"),
  };
}

function hideConfigWidget(cfg){
  if(!cfg) return;
  cfg.type = "string";
  cfg.visible = false;        // ComfyUI respecte ça
  cfg.hidden  = true;         // et LiteGraph aussi
  cfg.label = "";             // pas de label
  cfg.computeSize = ()=>[0,0];
  cfg.draw = ()=>{};          // no-op
  cfg.onDrawForeground = ()=>{};
  cfg.onDrawBackground = ()=>{};
  cfg.onMouse = ()=>false;
}

function ensureBottomOrder(node){
  const { ap, cp, as, cs, cfg } = getBottomBlock(node);
  hideConfigWidget(cfg);
  const arr = node.widgets;
  const order = [ap, cp, as, cs, cfg].filter(Boolean);
  // retire puis pousse à la fin dans cet ordre
  order.forEach(w => { const i=wIndex(node,w); if(i>=0) arr.splice(i,1); });
  order.forEach(w => arr.push(w));
  node.graph?.setDirtyCanvas(true);
}

// insère des widgets avant le bloc bas (prefix/suffix/config)
function insertBeforeBottom(node, widgets){
  const { ap, cp, as, cs, cfg } = getBottomBlock(node);
  const anchors = [ap, cp, as, cs, cfg].filter(Boolean);
  const arr = node.widgets;
  let insertAt = arr.length;
  if (anchors.length){
    const idxs = anchors.map(w=>wIndex(node,w)).filter(i=>i>=0);
    if (idxs.length) insertAt = Math.min(...idxs);
  }
  let pos = insertAt;
  widgets.forEach(w=>{
    const i=wIndex(node,w); if(i>=0) arr.splice(i,1);
    arr.splice(pos++,0,w);
  });
  ensureBottomOrder(node);
}

// ---------- Lignes dynamiques ----------
function addRowUI(node, initial, index){
  const rowId = index+1;

  const wFolder = node.addWidget("combo", `folder_${index}`, ROOT, null, { values:[ROOT] });
  wFolder.label = `Folder #${rowId}`;

  const wFile = node.addWidget("combo", `file_${index}`, "", null, { values:["(pick folder)"] });
  wFile.label = `File #${rowId}`;

  const wTemp = node.addWidget("number", `temperature_${index}`, 5, null, { min:0, max:10, step:1 });
  wTemp.label = `Temperature #${rowId} (0–10)`;

  insertBeforeBottom(node, [wFolder, wFile, wTemp]);

  const loadFolders = async ()=>{
    try{
      const dirs = await API.list_dirs(ROOT);
      setComboValues(wFolder, dirs, ROOT);
      if(!wFolder.value) wFolder.value = ROOT;
      wFolder.label = `Folder #${rowId}: ${prettyFolder(wFolder.value)}`;
    }catch(e){
      console.error("[MultiListMixer] list_dirs", e);
      setComboValues(wFolder,[ROOT],ROOT);
    }
    node.graph?.setDirtyCanvas(true);
  };
  const loadFiles = async ()=>{
    const dir = wFolder.value || ROOT;
    try{
      const files = await API.list_files(dir);
      setComboValues(wFile, files, "(no .txt/.csv here)");
    }catch(e){
      console.error("[MultiListMixer] list_files", e);
      setComboValues(wFile,["(error)"],"(error)");
    }
    node.graph?.setDirtyCanvas(true);
  };

  wFolder.callback = async ()=>{ await loadFiles(); saveConfig(node); wFolder.label = `Folder #${rowId}: ${prettyFolder(wFolder.value)}`; };
  wFile.callback   = async ()=>{ saveConfig(node); };
  wTemp.callback   = async ()=>{ saveConfig(node); };

  if(initial?.[index]){
    if(initial[index].folder) wFolder.value = initial[index].folder;
    if(typeof initial[index].temperature === "number") wTemp.value = initial[index].temperature;
  }
  setTimeout(async ()=>{
    await loadFolders(); await loadFiles();
    if(initial?.[index]?.file) wFile.value = initial[index].file;
    saveConfig(node);
  }, 20);
}

function removeLastRow(node){
  let n=0;
  for(let i=0;;i++){
    if(findW(node,`folder_${i}`) && findW(node,`file_${i}`) && findW(node,`temperature_${i}`)) n++; else break;
  }
  if(n<=2) return;
  const i=n-1, arr=node.widgets;
  [findW(node,`folder_${i}`), findW(node,`file_${i}`), findW(node,`temperature_${i}`)]
    .map(w=>wIndex(node,w)).filter(k=>k>=0).sort((a,b)=>b-a).forEach(k=>arr.splice(k,1));
  saveConfig(node);
  ensureBottomOrder(node);
}

// ---------- Boutons en haut (avant seed) ----------
function placeTopButtonsBeforeSeed(node, btnAdd, btnRem){
  const arr = node.widgets;
  // retire si déjà présents
  [btnAdd, btnRem].forEach(w=>{ const i=wIndex(node,w); if(i>=0) arr.splice(i,1); });
  // ancre: le widget 'seed' s'il existe
  let anchorIdx = -1;
  const seed = findW(node,"seed");
  if (seed) anchorIdx = wIndex(node, seed);
  // sinon, au tout début
  const insertAt = anchorIdx >= 0 ? anchorIdx : 0;
  arr.splice(insertAt, 0, btnAdd, btnRem);
  node.graph?.setDirtyCanvas(true);
}

// ---------- Extension ----------
app.registerExtension({
  name: "Orion4D.MasterPrompt.MultiListMixer",
  nodeCreated(node){
    if (node.constructor.type !== "multi_list_mixer") return;

    // Masquer/déplacer config_json au bas
    const wCfg = findW(node,"config_json");
    if (wCfg) hideConfigWidget(wCfg);

    // Crée d'abord les boutons (on les positionnera ensuite)
    const btnAdd = node.addWidget("button","➕ Add list",null,()=>{
      const state = readRows(node);
      addRowUI(node, state, state.length);
      saveConfig(node);
      // Après ajout, on repositionne les boutons
      placeTopButtonsBeforeSeed(node, btnAdd, btnRem);
    });
    const btnRem = node.addWidget("button","➖ Remove last (min 2)",null,()=>{
      removeLastRow(node);
      placeTopButtonsBeforeSeed(node, btnAdd, btnRem);
    });

    // Construit l'état initial (au moins 2 lignes)
    let initial=[];
    try{ const parsed = JSON.parse(wCfg?.value||"[]"); if(Array.isArray(parsed)) initial = parsed; }catch{}
    if (initial.length < 2) while (initial.length < 2) initial.push({ folder: ROOT, file: "", temperature: 5 });

    // Insère le bloc prefix/suffix tout en bas (et y inclut config_json)
    ensureBottomOrder(node);

    // Crée les lignes (elles s’insèrent avant le bloc bas)
    initial.forEach((_,i)=> addRowUI(node, initial, i));

    // Place définitivement les boutons en haut (avant seed)
    placeTopButtonsBeforeSeed(node, btnAdd, btnRem);

    // Labels propres
    btnAdd.label = "➕ Add list";
    btnRem.label = "➖ Remove last (min 2)";
  }
});
