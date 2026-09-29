import sys
from PySide6.QtWidgets import QApplication,QSystemTrayIcon
from .chrome_bridge import ChromeBridge
from .notifications import LillyAlert
from .task_engine import TaskEngine
from .tray import LillyTray

class LillyApplication:
    def __init__(self):
        self.app=QApplication(sys.argv);self.app.setApplicationName("Lilly");self.app.setQuitOnLastWindowClosed(False)
        self.active_alerts=[];self.paused=False;self.watched_tab=None;self.latest_capture=None;self.latest_price=None;self.task_engine=TaskEngine()
        if not QSystemTrayIcon.isSystemTrayAvailable():raise RuntimeError("Windows system tray is not available.")
        self.tray=LillyTray(self.app);self.tray.test_alert.connect(self.test_alert);self.tray.status_requested.connect(self.show_status)
        self.tray.pause_changed.connect(self.set_paused);self.tray.exit_requested.connect(self.shutdown);self.tray.set_task_count(self._active_task_count());self.tray.show()
        self.bridge=ChromeBridge(self.task_engine,parent=self.app);self.bridge.watch_started.connect(self.on_watch_started);self.bridge.watch_stopped.connect(self.on_watch_stopped)
        self.bridge.capture_received.connect(self.on_capture_received);self.bridge.task_created.connect(self.on_task_changed);self.bridge.task_deleted.connect(self.on_task_changed)
        self.bridge.price_observed.connect(self.on_price_observed);self.bridge.bridge_error.connect(self.on_bridge_error)
        if not self.bridge.start():self.show_alert("Lilly — Chrome Bridge Error","Could not start 127.0.0.1:8765. Another Lilly process may already be running.",force=True)
    def _active_task_count(self):return sum(1 for t in self.task_engine.list_tasks() if t.get("active"))
    def show_alert(self,title,message,force=False):
        if self.paused and not force:return
        a=LillyAlert(title,message);self.active_alerts.append(a)
        def remove():
            if a in self.active_alerts:self.active_alerts.remove(a)
        a.closed.connect(remove);a.show()
    def test_alert(self):self.show_alert("Lilly — Test Alert","Persistent alerts are working.",force=True)
    def show_status(self):
        state="PAUSED" if self.paused else "ACTIVE";chrome=f'Watching: {self.watched_tab.get("title","Untitled tab")}.' if self.watched_tab else "No Chrome tab selected."
        price=f" Latest live observation: {self.latest_price}." if self.latest_price is not None else " Waiting for live price."
        self.show_alert("Lilly — Status",f"Lilly is {state}. {chrome}{price} Active tasks: {self._active_task_count()}.",force=True)
    def set_paused(self,paused):self.paused=paused
    def on_watch_started(self,tab):
        self.watched_tab=tab;self.latest_capture=None;self.latest_price=None;self.tray.set_watched_tab(tab.get("title"))
        self.show_alert("Lilly — Live Monitor Ready",f'Watching: {tab.get("title","Untitled tab")}\nLilly will accept live TradingView price observations from this selected tab.',force=True)
    def on_watch_stopped(self):
        old=self.watched_tab.get("title") if self.watched_tab else "Chrome tab";self.watched_tab=None;self.latest_capture=None;self.latest_price=None;self.tray.set_watched_tab(None)
        self.show_alert("Lilly — Chrome Watch Stopped",f"Stopped watching: {old}",force=True)
    def on_capture_received(self,meta):self.latest_capture=meta;self.tray.set_last_capture(meta.get("captured_at","").replace("T"," "))
    def on_task_changed(self,*_):self.tray.set_task_count(self._active_task_count())
    def on_price_observed(self,value):
        self.latest_price=value;self.tray.set_live_price(value)
        if self.paused:return
        triggered=self.task_engine.evaluate_price(value);self.tray.set_task_count(self._active_task_count())
        for task in triggered:
            relation="at or above" if task["kind"]=="price_above" else "at or below";label=f' — {task["label"]}' if task.get("label") else ""
            self.show_alert("Lilly — Chart Condition Triggered",f'Live price {value} is {relation} {task["level"]}{label}.')
    def on_bridge_error(self,error):self.show_alert("Lilly — Chrome Bridge Error",error,force=True)
    def shutdown(self):
        self.bridge.stop()
        for a in list(self.active_alerts):a.close()
        self.tray.tray.hide();self.app.quit()
    def run(self):return self.app.exec()
def run():lilly=LillyApplication();sys.exit(lilly.run())
