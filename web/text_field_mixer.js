// Orion4D_MasterPrompt/web/text_field_mixer.js
// Text Field Mixer — lignes dynamiques (Enable + apercu + ✏️ Edit modal + Temp),
// entrées externes ext_text_1..12 : si linké, le champ devient "linked" (edit désactivé).
// Boutons +/− en haut, seed + contrôle juste dessous, prefix/suffix en bas.

import { app } from "/scripts/app.js";

const MAX_FIELDS = 12;

const findW = (node, name) => node.widgets?.find(w => w.name === name);
const wIndex = (node, w) => node.widgets.indexOf(w);
const debounce = (fn, t=80) => { let id; return (...a)=>{ clearTimeout(id); id=setTimeout(()=>fn(...a), t); }; };

// ---- inputs (sockets) helpers ----
function findInputSlot(node, name){
  if (!node.inputs) return { idx: -1, slot: null };
  const idx = node.inputs.findIndex(i => i?.name === name);
  return { idx, slot: idx >= 0 ? node.inputs[idx] : null };
}
function isInputLinked(node, name){
  const { slot } = findInputSlot(node, name);
  if (!slot) return false;
  // litegraph: slot.link (single) ou slot.links (multi)
  return !!(slot.link != null || (Array.isArray(slot.links) && slot.links.length));
}
function orderInputsSeedThenExt(node){
  if (!node.inputs || !node.inputs.length) return;
  const seedIdx = node.inputs.findIndex(i => i?.name === "seed");
  const extIdxs = [];
  const others = [];
  node.inputs.forEach((inp, i) => {
    if (!inp) return;
    if (inp.name === "seed") return;
    if (/^ext_text_\d+$/.test(inp.name)) extIdxs.push({ i, inp });
    else others.push({ i, inp });
  });
  // nouvel ordre: seed, ext_text_1..N (par num croissant), puis others
  extIdxs.sort((a,b) => {
    const ai = Number(a.inp.name.split("_").pop());
    const bi = Number(b.inp.name.split("_").pop());
    return ai - bi;
  });
  const newOrder = [];
  if (seedIdx >= 0) newOrder.push(node.inputs[seedIdx]);
  newOrder.push(...extIdxs.map(o => o.inp));
  newOrder.push(...others.map(o => o.inp));
  node.inputs = newOrder;
  node.size = node.computeSize(); // recalcul visuel
}

// ---------- Modal textarea ----------
function openTextareaModal(title, initialValue, onSave) {
  const overlay = document.createElement("div");
  overlay.style = "position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:99999;display:flex;align-items:center;justify-content:center;";
  const panel = document.createElement("div");
  panel.style = "width:min(900px,90vw);height:min(70vh,720px);background:#1e1e1e;color:#e0e0e0;border-radius:10px;box-shadow:0 20px 80px rgba(0,0,0,.5);display:flex;flex-direction:column;border:1px solid #2f2f2f;";
  const header = document.createElement("div");
  header.textContent = title || "Edit text";
  header.style = "padding:12px 14px;font-weight:600;border-bottom:1px solid #2f2f2f;";
  const area = document.createElement("textarea");
  area.value = initialValue ?? "";
  area.style = "flex:1;padding:12px 14px;resize:none;outline:none;border:none;background:#111;color:#e0e0e0;font-family:ui-monospace,Menlo,Consolas,monospace;line-height:1.35;font-size:13px;";
  const footer = document.createElement("div");
  footer.style = "padding:10px 12px;border-top:1px solid #2f2f2f;display:flex;gap:8px;justify-content:flex-end;";
  const btnCancel = document.createElement("button");
  btnCancel.textContent = "Cancel";
  btnCancel.style = "padding:6px 12px;background:#2b2b2b;color:#eee;border:1px solid #3a3a3a;border-radius:6px;cursor:pointer;";
  const btnOk = document.createElement("button");
  btnOk.textContent = "Save";
  btnOk.style = "padding:6px 12px;background:#3b82f6;color:#fff;border:1px solid #2563eb;border-radius:6px;cursor:pointer;";

  const close = () => document.body.removeChild(overlay);
  btnCancel.onclick = close;
  btnOk.onclick = () => { onSave?.(area.value ?? ""); close(); };
  overlay.onclick = (e) => { if (e.target === overlay) close(); };
  document.addEventListener("keydown", function esc(e){ if (e.key === "Escape") { close(); document.removeEventListener("keydown", esc); } });

  footer.append(btnCancel, btnOk);
  panel.append(header, area, footer);
  overlay.append(panel);
  document.body.appendChild(overlay);
  setTimeout(()=> area.focus(), 0);
}

// ---------- lecture/écriture config ----------
function countRows(node){
  let n=0;
  for(let i=0;;i++){
    if(findW(node,`enabled_${i}`) && findW(node,`text_${i}`) && findW(node,`edit_${i}`) && findW(node,`temperature_${i}`)) n++; else break;
  }
  return n;
}
function readRows(node){
  const rows=[];
  for(let i=0;;i++){
    const we=findW(node,`enabled_${i}`);
    const wt=findW(node,`text_${i}`);
    const tp=findW(node,`temperature_${i}`);
    if(!we||!wt||!tp) break;
    rows.push({
      enabled: !!we.value,
      text: (wt.value ?? "").toString(),
      temperature: Number.isFinite(tp.value) ? Number(tp.value) : 0
    });
  }
  return rows;
}
const saveConfig = debounce((node)=>{
  const wCfg = findW(node,"config_json"); if(!wCfg) return;
  const rows = readRows(node).map(r=>({
    enabled: !!r.enabled,
    text: r.text,
    temperature: Math.max(0, Math.min(10, Number(r.temperature)||0))
  }));
  wCfg.value = JSON.stringify(rows, null, 2);
  node.graph?.setDirtyCanvas(true);
}, 40);

// ---- seed / post-gen control ----
const getSeed = (node)=> findW(node,"seed");
function getPostGen(node){
  return node.widgets?.find(w=>{
    const L=(w?.label||"").toLowerCase();
    return (L.includes("contrô") && L.includes("génération")) || (L.includes("control") && L.includes("generation"));
  });
}
function placePostGenUnderSeed(node){
  const seed=getSeed(node), post=getPostGen(node); if(!seed || !post) return;
  const arr=node.widgets, i=wIndex(node,post), s=wIndex(node,seed);
  if(i === s+1) return;
  if(i>=0) arr.splice(i,1);
  arr.splice(s+1,0,post);
  node.graph?.setDirtyCanvas(true);
}

// ---- bloc bas (prefix/suffix + config_json) ----
function hideConfig(cfg){
  if(!cfg) return;
  cfg.type="string"; cfg.visible=false; cfg.hidden=true; cfg.label="";
  cfg.computeSize=()=>[0,0]; cfg.draw=()=>{}; cfg.onMouse=()=>false;
}
function pinBottom(node){
  const ap=findW(node,"add_prefix"), cp=findW(node,"custom_prefix");
  const as=findW(node,"add_suffix"), cs=findW(node,"custom_suffix");
  const cfg=findW(node,"config_json"); hideConfig(cfg);
  const arr=node.widgets, order=[ap,cp,as,cs,cfg].filter(Boolean);
  order.forEach(w=>{ const i=wIndex(node,w); if(i>=0) arr.splice(i,1); });
  order.forEach(w=>arr.push(w));
  node.graph?.setDirtyCanvas(true);
}

// ---- positionnements généraux ----
function btnsBeforeSeed(node, addBtn, remBtn){
  const arr=node.widgets;
  [addBtn, remBtn].forEach(w=>{ const i=wIndex(node,w); if(i>=0) arr.splice(i,1); });
  const seed=getSeed(node); const at=seed? wIndex(node,seed) : 0;
  arr.splice(at,0,addBtn,remBtn);
  node.graph?.setDirtyCanvas(true);
}
function rowBase(node){
  const seed=getSeed(node); if(!seed) return 0;
  const s=wIndex(node,seed); const post=getPostGen(node);
  return (post && wIndex(node,post)===s+1) ? s+2 : s+1;
}
function insertRow(node, widgets, rowIndex){
  const arr=node.widgets; let base=rowBase(node)+rowIndex*4; // enable, text, edit, temp
  widgets.forEach((w,k)=>{ const i=wIndex(node,w); if(i>=0) arr.splice(i,1); arr.splice(base+k,0,w); });
  node.graph?.setDirtyCanvas(true);
}

// ---- état "linked" d'une ligne (si ext_text_i connecté) ----
function refreshLinkedState(node, index){
  const edit = findW(node, `edit_${index}`);
  const text = findW(node, `text_${index}`);
  if (!edit || !text) return;

  const linked = isInputLinked(node, `ext_text_${index+1}`);
  edit.disabled = !!linked;
  edit.label = linked ? "linked" : "✏️ Edit";
  text.disabled = !!linked;
  node.graph?.setDirtyCanvas(true);
}

// ---- création d’une ligne ----
function addRowUI(node, initial, index){
  const rowId=index+1;

  const wEnable=node.addWidget("toggle",`enabled_${index}`,true,()=>saveConfig(node));
  wEnable.label=`Enable #${rowId}`;

  const wText=node.addWidget("string",`text_${index}`,"",()=>saveConfig(node));
  wText.label=`Text #${rowId}`;

  const wEdit=node.addWidget("button",`edit_${index}`,"✏️ Edit",()=> {
    if (wEdit.disabled) return;
    openTextareaModal(`Text #${rowId}`, wText.value || "", (val)=>{
      wText.value = val ?? "";
      saveConfig(node);
    });
  });

  const wTemp=node.addWidget("number",`temperature_${index}`,5,()=>saveConfig(node),{min:0,max:10,step:1});
  wTemp.label=`Temperature #${rowId} (0–10)`;

  insertRow(node, [wEnable, wText, wEdit, wTemp], index);

  const src=initial?.[index];
  if(src){
    if(typeof src.enabled==="boolean") wEnable.value=src.enabled;
    if(typeof src.text==="string") wText.value=src.text;
    if(typeof src.temperature==="number") wTemp.value=src.temperature;
  }

  // met à jour l'état linked au démarrage
  refreshLinkedState(node, index);
  saveConfig(node);
}

// ---- suppression ----
function removeLast(node){
  const n=countRows(node); if(n<=2) return;
  const i=n-1, arr=node.widgets;
  [findW(node,`enabled_${i}`), findW(node,`text_${i}`), findW(node,`edit_${i}`), findW(node,`temperature_${i}`)]
    .map(w=>wIndex(node,w)).filter(k=>k>=0).sort((a,b)=>b-a).forEach(k=>arr.splice(k,1));
  saveConfig(node);
}

// ---- extension ----
app.registerExtension({
  name:"Orion4D.MasterPrompt.TextFieldMixer",
  nodeCreated(node){
    if(node.constructor.type!=="text_field_mixer") return;

    // ordonne les entrées: seed, ext_text_1..N, puis autres
    orderInputsSeedThenExt(node);

    // hook: quand une connexion change, on met à jour l'état "linked"
    const oldOnConn = node.onConnectionsChange;
    node.onConnectionsChange = function(type, slotIndex, isConnected, link_info, input) {
      if (oldOnConn) oldOnConn.apply(this, arguments);
      // cherche si c'est un slot ext_text_k
      const slot = (this.inputs && this.inputs[slotIndex]) || null;
      if (slot && /^ext_text_(\d+)$/.test(slot.name)) {
        const k = Number(slot.name.split("_").pop()) - 1;
        refreshLinkedState(this, k);
      }
    };

    const cfg=findW(node,"config_json"); if(cfg){ cfg.visible=false; cfg.hidden=true; cfg.computeSize=()=>[0,0]; cfg.draw=()=>{}; }
    pinBottom(node);

    const btnAdd=node.addWidget("button","➕ Add field",null,()=>{
      const current=countRows(node);
      if (current >= MAX_FIELDS) { alert(`Max ${MAX_FIELDS} fields.`); return; }
      const init = readRows(node);
      addRowUI(node, init, current);
      orderInputsSeedThenExt(node);
      btnsBeforeSeed(node,btnAdd,btnRem);
      placePostGenUnderSeed(node);
    });
    const btnRem=node.addWidget("button","➖ Remove last (min 2)",null,()=>{
      removeLast(node);
      btnsBeforeSeed(node,btnAdd,btnRem);
      placePostGenUnderSeed(node);
    });

    // init (min 2)
    let initial=[];
    try{ const p=JSON.parse(cfg?.value||"[]"); if(Array.isArray(p)) initial=p; }catch{}
    if(initial.length<2) while(initial.length<2) initial.push({enabled:true,text:"",temperature:5});

    // seed-control juste sous seed
    placePostGenUnderSeed(node);

    // lignes
    initial.forEach((_,i)=> addRowUI(node, initial, i));

    // boutons en haut
    btnsBeforeSeed(node,btnAdd,btnRem);
    placePostGenUnderSeed(node);
    pinBottom(node);

    btnAdd.label="➕ Add field";
    btnRem.label="➖ Remove last (min 2)";
  }
});
