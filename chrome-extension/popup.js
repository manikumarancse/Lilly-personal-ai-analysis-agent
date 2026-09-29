const API="http://127.0.0.1:8765";
let currentTab=null, watching=null;

async function getCurrentTab(){
  const tabs=await chrome.tabs.query({active:true,currentWindow:true});
  currentTab=tabs[0]||null;
  tabTitle.textContent=currentTab?.title||"No active tab";
  tabUrl.textContent=currentTab?.url||"";
}
async function request(path,options={}){
  const r=await fetch(API+path,options); const d=await r.json();
  if(!r.ok) throw new Error(d.error||"Lilly returned an error"); return d;
}
async function post(path,payload={}){
  return request(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
}
async function refresh(){
  try{
    const d=await request("/health"); watching=d.watching;
    connection.textContent=watching?"● Lilly connected — chart selected":"● Lilly connected";
    connection.className="status online";
    watch.disabled=false; capture.disabled=!watching; stop.disabled=!watching;
    renderTasks(d.tasks||[]);
  }catch(e){
    connection.textContent="● Lilly desktop app is not connected"; connection.className="status offline";
    watch.disabled=capture.disabled=stop.disabled=true;
  }
}
function renderTasks(items){
  if(!items.length){tasks.textContent="No tasks yet.";return;}
  tasks.innerHTML="";
  items.slice().reverse().forEach(t=>{
    const row=document.createElement("div"); row.className="task"+(t.triggered?" triggered":"");
    const relation=t.kind==="price_above"?">=":"<=";
    row.append(document.createTextNode(`${t.label||"Price watch"}: ${relation} ${t.level} — ${t.triggered?"TRIGGERED":t.active?"ACTIVE":"INACTIVE"}`));
    const b=document.createElement("button"); b.className="delete"; b.textContent="Delete";
    b.onclick=async()=>{await request("/tasks/"+t.id,{method:"DELETE"}); await refresh();};
    row.appendChild(b); tasks.appendChild(row);
  });
}
watch.onclick=async()=>{try{await post("/watch",{tab_id:currentTab.id,title:currentTab.title,url:currentTab.url});message.textContent="Tab selected.";await refresh();}catch(e){message.textContent=e.message;}};
stop.onclick=async()=>{try{await post("/stop");message.textContent="Monitoring stopped.";await refresh();}catch(e){message.textContent=e.message;}};
capture.onclick=async()=>{
  try{
    if(currentTab.id!==watching?.tab_id) throw new Error("Open the watched tab before capturing.");
    const image_data=await chrome.tabs.captureVisibleTab(currentTab.windowId,{format:"jpeg",quality:85});
    await post("/capture",{tab_id:currentTab.id,title:currentTab.title,url:currentTab.url,image_data,width:screen.width,height:screen.height});
    message.textContent="Chart capture saved.";
  }catch(e){message.textContent=e.message;}
};
addTask.onclick=async()=>{
  try{
    if(!level.value) throw new Error("Enter a price level.");
    await post("/tasks",{kind:kind.value,level:Number(level.value),label:label.value});
    level.value=""; label.value=""; message.textContent="Watch task added."; await refresh();
  }catch(e){message.textContent=e.message;}
};
sendPrice.onclick=async()=>{
  try{
    if(!observedPrice.value) throw new Error("Enter a test price.");
    await post("/observe/price",{value:Number(observedPrice.value)});
    message.textContent="Observation sent to Lilly."; await refresh();
  }catch(e){message.textContent=e.message;}
};
(async()=>{await getCurrentTab();await refresh();})();
