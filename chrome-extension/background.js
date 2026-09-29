const API="http://127.0.0.1:8765";
let watchedTabId=null;
let lastPrice=null;
let timer=null;

function parseNumber(text){
  if(!text) return null;
  const m=String(text).replace(/\u2212/g,"-").match(/-?\d[\d,]*(?:\.\d+)?/);
  if(!m) return null;
  const n=Number(m[0].replace(/,/g,""));
  return Number.isFinite(n)?n:null;
}

async function readTradingViewPrice(tabId){
  try{
    const results=await chrome.scripting.executeScript({
      target:{tabId},
      func:()=>{
        const candidates=[];
        const selectors=[
          '[data-field="last"]',
          '[data-name="legend-source-item"]',
          '[class*="lastValue"]',
          '[class*="price-axis"]',
          '[class*="valuesWrapper"]'
        ];
        for(const sel of selectors){
          document.querySelectorAll(sel).forEach(el=>{
            const text=(el.innerText||el.textContent||"").trim();
            if(text) candidates.push(text);
          });
        }
        const title=document.title||"";
        const bodyText=document.body?.innerText||"";
        const topText=bodyText.slice(0,5000);
        return {candidates,title,topText};
      }
    });
    const data=results?.[0]?.result;
    if(!data) return null;

    // TradingView legend commonly contains O/H/L/C. Prefer the C (close/current) value.
    for(const text of data.candidates){
      const c=text.match(/(?:^|\s)C\s*([\d,]+(?:\.\d+)?)/i);
      if(c){ const n=parseNumber(c[1]); if(n!==null) return n; }
    }
    for(const text of data.candidates){
      const n=parseNumber(text);
      if(n!==null && n>0) return n;
    }
    const c=data.topText.match(/(?:^|\s)C\s*([\d,]+(?:\.\d+)?)/im);
    return c?parseNumber(c[1]):null;
  }catch(e){ return null; }
}

async function sendPrice(price){
  try{
    await fetch(API+"/observe/price",{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({value:price,source:"tradingview_dom",tab_id:watchedTabId})
    });
  }catch(e){}
}

async function tick(){
  if(watchedTabId===null) return;
  try{
    const tab=await chrome.tabs.get(watchedTabId);
    if(!tab?.url?.includes("tradingview.com")) return;
    const price=await readTradingViewPrice(watchedTabId);
    if(price!==null && price!==lastPrice){
      lastPrice=price;
      await chrome.storage.local.set({lillyLastPrice:price,lillyLastPriceAt:new Date().toISOString()});
      await sendPrice(price);
    }
  }catch(e){}
}

function start(){
  if(timer) clearInterval(timer);
  timer=setInterval(tick,2000);
  tick();
}
function stop(){
  if(timer) clearInterval(timer);
  timer=null; watchedTabId=null; lastPrice=null;
}

chrome.runtime.onMessage.addListener((msg,sender,sendResponse)=>{
  if(msg.type==="START_LIVE_MONITOR"){
    watchedTabId=msg.tabId; lastPrice=null; start();
    sendResponse({ok:true});
  }else if(msg.type==="STOP_LIVE_MONITOR"){
    stop(); sendResponse({ok:true});
  }else if(msg.type==="LIVE_STATUS"){
    chrome.storage.local.get(["lillyLastPrice","lillyLastPriceAt"]).then(s=>{
      sendResponse({ok:true,watchedTabId,lastPrice:s.lillyLastPrice??null,lastPriceAt:s.lillyLastPriceAt??null});
    });
    return true;
  }
});

chrome.runtime.onStartup.addListener(()=>{ stop(); });
