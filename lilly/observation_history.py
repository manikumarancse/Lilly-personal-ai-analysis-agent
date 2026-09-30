import json
import threading
from datetime import datetime
from pathlib import Path

class ObservationHistory:
    def __init__(self,data_dir="data",max_items=5000):
        self.path=Path(data_dir)/"observations.jsonl";self.path.parent.mkdir(parents=True,exist_ok=True)
        self.max_items=max_items;self._lock=threading.Lock()
    def add_price(self,value,tab=None,source="chart"):
        item={"observed_at":datetime.now().isoformat(timespec="seconds"),"type":"price","value":float(value),"source":source,
              "tab_id":(tab or {}).get("tab_id"),"title":(tab or {}).get("title"),"url":(tab or {}).get("url")}
        with self._lock:
            with self.path.open("a",encoding="utf-8") as f:f.write(json.dumps(item,ensure_ascii=False)+"\n")
        return item
    def recent(self,limit=100):
        if not self.path.exists():return []
        with self._lock:
            lines=self.path.read_text(encoding="utf-8").splitlines()[-max(1,min(int(limit),1000)):]
        out=[]
        for line in lines:
            try:out.append(json.loads(line))
            except json.JSONDecodeError:pass
        return out
    def summary(self,limit=500):
        items=[x for x in self.recent(limit) if x.get("type")=="price"]
        tasks=[]
        if not items:return {"count":0,"latest":None,"first":None,"high":None,"low":None,"change":None,"from":None,"to":None}
        vals=[float(x["value"]) for x in items]
        return {"count":len(items),"latest":vals[-1],"first":vals[0],"high":max(vals),"low":min(vals),
                "change":vals[-1]-vals[0],"from":items[0].get("observed_at"),"to":items[-1].get("observed_at")}
