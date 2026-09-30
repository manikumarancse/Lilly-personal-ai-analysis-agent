import json,threading,uuid
from datetime import datetime
from pathlib import Path
class ObservationHistory:
    def __init__(self,data_dir="data",max_items=5000):
        self.path=Path(data_dir)/"observations.jsonl";self.path.parent.mkdir(parents=True,exist_ok=True);self.max_items=max_items;self._lock=threading.Lock();self._session=None
    @property
    def current_session(self):return dict(self._session) if self._session else None
    def start_session(self,tab=None,reason="watch_started"):
        self._session={"id":uuid.uuid4().hex[:12],"started_at":datetime.now().isoformat(timespec="seconds"),"reason":reason,"tab_id":(tab or {}).get("tab_id"),"title":(tab or {}).get("title"),"url":(tab or {}).get("url")};return dict(self._session)
    def add_price(self,value,tab=None,source="chart"):
        if not self._session:self.start_session(tab,"first_observation")
        item={"observed_at":datetime.now().isoformat(timespec="seconds"),"type":"price","value":float(value),"source":source,"session_id":self._session["id"],"tab_id":(tab or {}).get("tab_id"),"title":(tab or {}).get("title"),"url":(tab or {}).get("url")}
        with self._lock:
            with self.path.open("a",encoding="utf-8") as f:f.write(json.dumps(item,ensure_ascii=False)+"\n")
        return item
    def recent(self,limit=100,session_id=None):
        if not self.path.exists():return []
        with self._lock:lines=self.path.read_text(encoding="utf-8").splitlines()
        out=[]
        for line in reversed(lines):
            try:x=json.loads(line)
            except json.JSONDecodeError:continue
            if session_id and x.get("session_id")!=session_id:continue
            out.append(x)
            if len(out)>=max(1,min(int(limit),1000)):break
        return list(reversed(out))
    def summary(self,limit=1000,session_id=None):
        sid=session_id or (self._session or {}).get("id");items=[x for x in self.recent(limit,sid) if x.get("type")=="price"];base={"session":self.current_session,"count":0,"latest":None,"first":None,"high":None,"low":None,"change":None,"from":None,"to":None}
        if not items:return base
        vals=[float(x["value"]) for x in items];base.update({"count":len(items),"latest":vals[-1],"first":vals[0],"high":max(vals),"low":min(vals),"change":vals[-1]-vals[0],"from":items[0].get("observed_at"),"to":items[-1].get("observed_at")});return base
