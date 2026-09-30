import base64,json,threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from PySide6.QtCore import QObject,Signal
from .chart_analyzer import ChartAnalyzer
from .market_data import CandleStore, MarketStructureAnalyzer

class ChromeBridge(QObject):
    watch_started=Signal(dict);watch_stopped=Signal();capture_received=Signal(dict);task_created=Signal(dict);task_deleted=Signal(str);price_observed=Signal(float);bridge_error=Signal(str)
    def __init__(self,task_engine,history,host="127.0.0.1",port=8765,parent=None):
        super().__init__(parent);self.task_engine=task_engine;self.history=history;self.host=host;self.port=port;self._server=None;self._thread=None
        self._watched_tab=None;self._latest_capture=None;self._latest_price=None;self._latest_price_at=None;self._lock=threading.Lock();self.analyzer=ChartAnalyzer();self.candles=CandleStore();self.structure_analyzer=MarketStructureAnalyzer()
        self.capture_dir=Path("data")/"captures";self.capture_dir.mkdir(parents=True,exist_ok=True)
    @property
    def watched_tab(self):
        with self._lock:return dict(self._watched_tab) if self._watched_tab else None
    @property
    def latest_capture(self):
        with self._lock:return dict(self._latest_capture) if self._latest_capture else None
    @property
    def latest_price(self):
        with self._lock:return self._latest_price
    @property
    def latest_price_at(self):
        with self._lock:return self._latest_price_at
    def _save_capture(self,body):
        data_url=body.get("image_data","")
        if not data_url.startswith("data:image/") or "," not in data_url:raise ValueError("Missing or invalid image_data")
        header,encoded=data_url.split(",",1);extension="png" if "png" in header else "jpg";image_bytes=base64.b64decode(encoded,validate=True)
        if len(image_bytes)>15*1024*1024:raise ValueError("Capture is too large")
        now=datetime.now();image_path=self.capture_dir/f"latest_chart.{extension}";image_path.write_bytes(image_bytes)
        meta={"captured_at":now.isoformat(timespec="seconds"),"path":str(image_path.resolve()),"bytes":len(image_bytes),"tab_id":body.get("tab_id"),"title":str(body.get("title") or "Untitled tab")[:300],"url":str(body.get("url") or "")[:3000],"width":body.get("width"),"height":body.get("height")}
        (self.capture_dir/"latest_chart.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
        with self._lock:self._latest_capture=meta
        self.capture_received.emit(meta);return meta
    def start(self):
        bridge=self
        class Handler(BaseHTTPRequestHandler):
            def _headers(self,status=200):
                self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Methods","GET, POST, DELETE, OPTIONS");self.send_header("Access-Control-Allow-Headers","Content-Type");self.end_headers()
            def _json(self,payload,status=200):self._headers(status);self.wfile.write(json.dumps(payload).encode("utf-8"))
            def _body(self):length=int(self.headers.get("Content-Length","0"));return json.loads(self.rfile.read(length) or b"{}")
            def do_OPTIONS(self):self._headers(204)
            def do_GET(self):
                parsed=urlparse(self.path);path=parsed.path
                if path=="/health":self._json({"ok":True,"service":"lilly","version":"0.10.0","watching":bridge.watched_tab,"latest_capture":bridge.latest_capture,"latest_price":bridge.latest_price,"latest_price_at":bridge.latest_price_at,"tasks":bridge.task_engine.list_tasks()})
                elif path=="/tasks":self._json({"ok":True,"tasks":bridge.task_engine.list_tasks()})
                elif path=="/capture/latest":self._json({"ok":True,"capture":bridge.latest_capture})
                elif path=="/observations":
                    limit=parse_qs(parsed.query).get("limit",["100"])[0]
                    try:limit=int(limit)
                    except ValueError:limit=100
                    self._json({"ok":True,"observations":bridge.history.recent(limit)})
                elif path=="/market/context":
                    self._json({"ok":True,"context":bridge.candles.context,"candles":len(bridge.candles.list())})
                elif path=="/market/structure":
                    self._json({"ok":True,"analysis":bridge.structure_analyzer.analyze(bridge.candles)})
                elif path=="/analysis":
                    self._json({"ok":True,"analysis":bridge.analyzer.analyze(bridge.history)})
                elif path=="/update":
                    s=bridge.history.summary();tasks=bridge.task_engine.list_tasks();active=sum(1 for t in tasks if t.get("active"));started=(bridge.history.current_session or {}).get("started_at","");triggered=sum(1 for t in tasks if t.get("triggered") and (not started or (t.get("triggered_at") or "")>=started))
                    s.update({"active_tasks":active,"triggered_tasks":triggered,"watching":bridge.watched_tab});self._json({"ok":True,"update":s})
                else:self._json({"ok":False,"error":"Not found"},404)
            def do_POST(self):
                try:body=self._body()
                except json.JSONDecodeError:self._json({"ok":False,"error":"Invalid JSON"},400);return
                if self.path=="/watch":
                    tab={"tab_id":body.get("tab_id"),"title":str(body.get("title") or "Untitled tab")[:300],"url":str(body.get("url") or "")[:3000]}
                    with bridge._lock:bridge._watched_tab=tab;bridge._latest_price=None;bridge._latest_price_at=None
                    session=bridge.history.start_session(tab,"watch_started");bridge.watch_started.emit(tab);self._json({"ok":True,"watching":tab,"session":session})
                elif self.path=="/session/reset":
                    watched=bridge.watched_tab
                    if not watched:self._json({"ok":False,"error":"No tab is being watched"},409);return
                    session=bridge.history.start_session(watched,"manual_reset")
                    with bridge._lock:bridge._latest_price=None;bridge._latest_price_at=None
                    self._json({"ok":True,"session":session})
                elif self.path=="/stop":
                    with bridge._lock:bridge._watched_tab=None
                    bridge.watch_stopped.emit();self._json({"ok":True,"watching":None})
                elif self.path=="/capture":
                    watched=bridge.watched_tab
                    if not watched:self._json({"ok":False,"error":"No tab is being watched"},409);return
                    if body.get("tab_id")!=watched.get("tab_id"):self._json({"ok":False,"error":"Capture is not from the selected tab"},403);return
                    try:meta=bridge._save_capture(body)
                    except (ValueError,TypeError,base64.binascii.Error) as exc:self._json({"ok":False,"error":str(exc)},400);return
                    self._json({"ok":True,"capture":meta})
                elif self.path=="/market/context":
                    context,changed=bridge.candles.set_context(str(body.get("symbol") or "")[:100] or None,str(body.get("timeframe") or "")[:30] or None);self._json({"ok":True,"context":context,"changed":changed})
                elif self.path=="/market/candles":
                    candles=body.get("candles")
                    if not isinstance(candles,list):self._json({"ok":False,"error":"candles must be a list"},400);return
                    try:count=bridge.candles.replace(candles)
                    except (KeyError,ValueError,TypeError) as exc:self._json({"ok":False,"error":"Invalid OHLC candle: "+str(exc)},400);return
                    self._json({"ok":True,"candles":count})
                elif self.path=="/tasks":
                    try:task=bridge.task_engine.add_task(body.get("kind"),body.get("level"),body.get("label",""))
                    except (ValueError,TypeError) as exc:self._json({"ok":False,"error":str(exc)},400);return
                    bridge.task_created.emit(task);self._json({"ok":True,"task":task},201)
                elif self.path=="/observe/price":
                    try:value=float(body.get("value"))
                    except (ValueError,TypeError):self._json({"ok":False,"error":"A numeric price is required"},400);return
                    watched=bridge.watched_tab;supplied_tab=body.get("tab_id")
                    if supplied_tab is not None and watched and supplied_tab!=watched.get("tab_id"):self._json({"ok":False,"error":"Price is not from the selected tab"},403);return
                    item=bridge.history.add_price(value,watched,body.get("source","chart"));now=item["observed_at"]
                    with bridge._lock:bridge._latest_price=value;bridge._latest_price_at=now
                    bridge.price_observed.emit(value);self._json({"ok":True,"value":value,"observed_at":now})
                else:self._json({"ok":False,"error":"Not found"},404)
            def do_DELETE(self):
                if self.path.startswith("/tasks/"):
                    task_id=self.path.rsplit("/",1)[-1]
                    if bridge.task_engine.delete_task(task_id):bridge.task_deleted.emit(task_id);self._json({"ok":True})
                    else:self._json({"ok":False,"error":"Task not found"},404)
                else:self._json({"ok":False,"error":"Not found"},404)
            def log_message(self,format,*args):return
        try:self._server=ThreadingHTTPServer((self.host,self.port),Handler)
        except OSError as exc:self.bridge_error.emit(str(exc));return False
        self._thread=threading.Thread(target=self._server.serve_forever,name="LillyChromeBridge",daemon=True);self._thread.start();return True
    def stop(self):
        if self._server:self._server.shutdown();self._server.server_close();self._server=None
        self._thread=None
