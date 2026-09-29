from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

def make_lilly_icon(active=True):
    p=QPixmap(64,64);p.fill(QColor(0,0,0,0));q=QPainter(p);q.setRenderHint(QPainter.Antialiasing)
    q.setBrush(QColor("#12B76A") if active else QColor("#98A2B3"));q.setPen(QColor("#FFFFFF"));q.drawEllipse(5,5,54,54)
    f=q.font();f.setBold(True);f.setPointSize(24);q.setFont(f);q.drawText(p.rect(),0x84,"L");q.end();return QIcon(p)

class LillyTray(QObject):
    test_alert=Signal();status_requested=Signal();pause_changed=Signal(bool);exit_requested=Signal()
    def __init__(self,parent=None):
        super().__init__(parent);self.paused=False;self.watched_title=None;self.last_capture=None;self.task_count=0;self.live_price=None
        self.tray=QSystemTrayIcon(make_lilly_icon(True),parent);menu=QMenu()
        self.status_action=QAction();self.status_action.setEnabled(False);menu.addAction(self.status_action)
        self.watch_action=QAction();self.watch_action.setEnabled(False);menu.addAction(self.watch_action)
        self.price_action=QAction();self.price_action.setEnabled(False);menu.addAction(self.price_action)
        self.tasks_action=QAction();self.tasks_action.setEnabled(False);menu.addAction(self.tasks_action)
        menu.addSeparator();a=QAction("Test persistent alert");a.triggered.connect(self.test_alert.emit);menu.addAction(a)
        a=QAction("Show Lilly status");a.triggered.connect(self.status_requested.emit);menu.addAction(a)
        self.pause_action=QAction();self.pause_action.triggered.connect(self.toggle_pause);menu.addAction(self.pause_action)
        menu.addSeparator();a=QAction("Exit Lilly");a.triggered.connect(self.exit_requested.emit);menu.addAction(a)
        self.tray.setContextMenu(menu);self._refresh()
    def show(self):self.tray.show()
    def set_watched_tab(self,title=None):self.watched_title=title;self.live_price=None;self._refresh()
    def set_last_capture(self,captured_at=None):self.last_capture=captured_at;self._refresh()
    def set_task_count(self,count):self.task_count=count;self._refresh()
    def set_live_price(self,price):self.live_price=price;self._refresh()
    def toggle_pause(self):self.paused=not self.paused;self._refresh();self.pause_changed.emit(self.paused)
    def _refresh(self):
        if self.paused:self.status_action.setText("● Lilly is Paused");self.pause_action.setText("Resume Lilly");self.tray.setIcon(make_lilly_icon(False));base="Lilly • Paused"
        else:self.status_action.setText("● Lilly is Active");self.pause_action.setText("Pause Lilly");self.tray.setIcon(make_lilly_icon(True));base="Lilly • Active"
        if self.watched_title:
            short=self.watched_title[:45]+("…" if len(self.watched_title)>45 else "");self.watch_action.setText(f"Chrome: Watching {short}");self.tray.setToolTip(f"{base} • Live monitoring")
        else:self.watch_action.setText("Chrome: No tab selected");self.tray.setToolTip(base)
        self.price_action.setText(f"Live price: {self.live_price}" if self.live_price is not None else "Live price: Waiting")
        self.tasks_action.setText(f"Tasks: {self.task_count} active")
