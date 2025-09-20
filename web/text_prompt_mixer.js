"use strict";
import { app } from "/scripts/app.js";

const MAX_FIELDS = 12;
const findW = (n, name) => n.widgets?.find(w => w.name === name);
const wIndex = (n, w) => n.widgets.indexOf(w);
const debounce = (fn,t=80)=>{let id;return(...a)=>{clearTimeout(id);id=setTimeout(()=>fn(...a),t);};};

function findInputSlot(n, name){ if(!n.inputs) return {idx:-1,slot:null}; const idx=n.inputs.findIndex(i=>i?.name===name); return {idx,slot:idx>=0?n.inputs[idx]:null}; }
function isInputLinked(n, name){ const {slot}=findInputSlot(n,name); if(!slot) return false; return !!(slot.link!=null || (Array.isArray(slot.links)&&slot.links.length)); }

function openTextareaModal(title, val, onSave){
  const ov=document.createElement("div"); ov.style="position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:99999;display:flex;align-items:center;justify-content:center;";
  const p=document.createElement("div"); p.style="width:min(900px,90vw);height:min(70vh,720px);background:#1e1e1e;color:#e0e0e0;border-radius:10px;box-shadow:0 20px 80px rgba(0,0,0,.5);display:flex;flex-direction:column;border:1px solid #2f2f2f;";
  const h=document.createElement("div"); h.textContent=title||"Edit text"; h.style="padding:12px 14px;font-weight:600;border-bottom:1px solid #2f2f2f;";
  const a=document.createElement("textarea"); a.value=val??""; a.style="flex:1;padding:12px 14px;resize:none;outline:none;border:none;background:#111;color:#e0e0e0;font-family:ui-monospace,Menlo,Consolas,monospace;";
  const f=document.createElement("div"); f.style="padding:10px 12px;border-top:1px solid #2f2f2f;display:flex;gap:8px;justify-content:flex-end;";
  const c=document.createElement("button"); c.textContent="Cancel"; c.style="padding:6px 12px;background:#2b2b2b;color:#eee;border:1px solid #3a3a3a;border-radius:6px;cursor:pointer;";
  const ok=document.createElement("button"); ok.textContent="Save"; ok.style="padding:6px 12px;background:#3b82f6;color:#fff;border:1px solid #2563eb;border-radius:6px;cursor:pointer;";
  const close=()=>document.body.removeChild(ov); c.onclick=close; ok.onclick=()=>{onSave?.(a.value??"");close();}; ov.onclick=e=>{if(e.target===ov)close();};
  f.append(c,ok); p.append(h,a,f); ov.append(p); document.body.appendChild(ov); setTimeout(()=>a.focus(),0);
}

function countRows(n){ let k=0; for(;;k++){ if(findW(n,`enabled_${k}`)&&findW(n,`text_${k}`)&&findW(n,`edit_${k}`)&&findW(n,`sep_${k}`)) continue; break; } return k; }
function readRows(n){
  const rows=[]; for(let i=0;;i++){ const we=findW(n,`enabled_${i}`),wt=findW(n,`text_${i}`),ws=findW(n,`sep_${i}`); if(!we||!wt||!ws) break;
    rows.push({enabled:!!we.value,text:(wt.value??"").toString(),sep:(ws.value??"").toString()}); } return rows;
}
const saveConfig = debounce((n)=>{ const w=findW(n,"config_json"); if(!w) return; w.value=JSON.stringify(readRows(n),null,2); n.graph?.setDirtyCanvas(true); },40);

function hideConfig(w){ if(!w) return; w.visible=false; w.hidden=true; w.computeSize=()=>[0,0]; w.draw=()=>{}; }
function pinBottom(n){
  const ap=findW(n,"add_prefix"),cp=findW(n,"custom_prefix"),as=findW(n,"add_suffix"),cs=findW(n,"custom_suffix"),cfg=findW(n,"config_json"); hideConfig(cfg);
  const arr=n.widgets, order=[ap,cp,as,cs,cfg].filter(Boolean);
  order.forEach(w=>{ const i=wIndex(n,w); if(i>=0) arr.splice(i,1); }); order.forEach(w=>arr.push(w)); n.graph?.setDirtyCanvas(true);
}
function insertBeforeBottom(n, ws){
  const anchors=[findW(n,"add_prefix"),findW(n,"custom_prefix"),findW(n,"add_suffix"),findW(n,"custom_suffix"),findW(n,"config_json")].filter(Boolean);
  const arr=n.widgets; let at=arr.length; if(anchors.length){ const idxs=anchors.map(w=>wIndex(n,w)).filter(i=>i>=0); if(idxs.length) at=Math.min(...idxs); }
  let pos=at; ws.forEach(w=>{ const i=wIndex(n,w); if(i>=0) arr.splice(i,1); arr.splice(pos++,0,w); }); pinBottom(n);
}

function refreshLinked(n,i){ const e=findW(n,`edit_${i}`), t=findW(n,`text_${i}`); if(!e||!t) return; const linked=isInputLinked(n,`ext_text_${i+1}`); e.disabled=!!linked; e.label=linked?"linked":"✏️ Edit"; t.disabled=!!linked; n.graph?.setDirtyCanvas(true); }

function addRow(n, initial, i){
  const id=i+1;
  const wE=n.addWidget("toggle",`enabled_${i}`,true,()=>saveConfig(n)); wE.label=`Enable #${id}`;
  const wT=n.addWidget("string",`text_${i}`,"",()=>saveConfig(n)); wT.label=`Text #${id}`;
  const wB=n.addWidget("button",`edit_${i}`,"✏️ Edit",()=>{ if(wB.disabled) return; openTextareaModal(`Text #${id}`, wT.value||"", v=>{ wT.value=v??""; saveConfig(n); }); });
  const wS=n.addWidget("string",`sep_${i}`,"",()=>saveConfig(n)); wS.label=`Sep #${id} (ex: ", " ou "\\n")`;
  insertBeforeBottom(n,[wE,wT,wB,wS]);
  const src=initial?.[i]; if(src){ if(typeof src.enabled==="boolean") wE.value=src.enabled; if(typeof src.text==="string") wT.value=src.text; if(typeof src.sep==="string") wS.value=src.sep; }
  refreshLinked(n,i); saveConfig(n);
}

function removeLast(n){ const k=countRows(n); if(k<=2) return; const i=k-1, arr=n.widgets;
  [findW(n,`enabled_${i}`),findW(n,`text_${i}`),findW(n,`edit_${i}`),findW(n,`sep_${i}`)]
    .map(w=>wIndex(n,w)).filter(x=>x>=0).sort((a,b)=>b-a).forEach(x=>arr.splice(x,1)); saveConfig(n); pinBottom(n);
}

function orderInputs(n){ if(!n.inputs?.length) return; const ext=[],other=[]; n.inputs.forEach(inp=>{ if(!inp) return; (/^ext_text_\d+$/).test(inp.name)?ext.push(inp):other.push(inp); });
  ext.sort((a,b)=>Number(a.name.split("_").pop())-Number(b.name.split("_").pop())); n.inputs=[...ext,...other]; n.size=n.computeSize();
}

app.registerExtension({
  name:"Orion4D.MasterPrompt.TextPromptMixer",
  nodeCreated(node){
    if(node.constructor.type!=="text_prompt_mixer") return;

    orderInputs(node);

    const old = node.onConnectionsChange;
    node.onConnectionsChange=function(type,slotIndex,isConnected,link_info,input){
      if(old) old.apply(this,arguments);
      const slot=(this.inputs&&this.inputs[slotIndex])||null;
      if(slot && /^ext_text_(\d+)$/.test(slot.name)){ const k=Number(slot.name.split("_").pop())-1; refreshLinked(this,k); }
    };

    const cfg=findW(node,"config_json"); if(cfg){ hideConfig(cfg); }
    pinBottom(node);

    const add=node.addWidget("button","➕ Add field",null,()=>{ const cur=countRows(node); if(cur>=MAX_FIELDS){ alert(`Max ${MAX_FIELDS} fields.`); return; } const init=readRows(node); addRow(node,init,cur); placeTopButtons(node,add,rem); });
    const rem=node.addWidget("button","➖ Remove last (min 2)",null,()=>{ removeLast(node); placeTopButtons(node,add,rem); });

    let initial=[]; try{ const p=JSON.parse(cfg?.value||"[]"); if(Array.isArray(p)) initial=p; }catch{}
    if(initial.length<2) while(initial.length<2) initial.push({enabled:true,text:"",sep:""});
    initial.forEach((_,i)=>addRow(node,initial,i));

    placeTopButtons(node,add,rem);
  }
});

function placeTopButtons(n,a,b){ const arr=n.widgets; [a,b].forEach(w=>{ const i=wIndex(n,w); if(i>=0) arr.splice(i,1); }); arr.splice(0,0,a,b); n.graph?.setDirtyCanvas(true); }
