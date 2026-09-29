from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def make_lilly_icon(active=True):
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#12B76A") if active else QColor("#98A2B3"))
    painter.setPen(QColor("#FFFFFF"))
    painter.drawEllipse(5, 5, 54, 54)
    font = painter.font()
    font.setBold(True)
    font.setPointSize(24)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x84, "L")
    painter.end()
    return QIcon(pixmap)


class LillyTray(QObject):
    test_alert = Signal()
    status_requested = Signal()
    pause_changed = Signal(bool)
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paused = False
        self.watched_title = None
        self.last_capture = None
        self.task_count = 0
        self.tray = QSystemTrayIcon(make_lilly_icon(True), parent)
        menu = QMenu()
        self.status_action = QAction()
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        self.watch_action = QAction()
        self.watch_action.setEnabled(False)
        menu.addAction(self.watch_action)
        self.capture_action = QAction()
        self.capture_action.setEnabled(False)
        menu.addAction(self.capture_action)
        self.tasks_action = QAction()
        self.tasks_action.setEnabled(False)
        menu.addAction(self.tasks_action)
        menu.addSeparator()
        test_action = QAction("Test persistent alert")
        test_action.triggered.connect(self.test_alert.emit)
        menu.addAction(test_action)
        status_action = QAction("Show Lilly status")
        status_action.triggered.connect(self.status_requested.emit)
        menu.addAction(status_action)
        self.pause_action = QAction()
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)
        menu.addSeparator()
        exit_action = QAction("Exit Lilly")
        exit_action.triggered.connect(self.exit_requested.emit)
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self._refresh()

    def show(self):
        self.tray.show()

    def set_watched_tab(self, title=None):
        self.watched_title = title
        if not title:
            self.last_capture = None
        self._refresh()

    def set_last_capture(self, captured_at=None):
        self.last_capture = captured_at
        self._refresh()

    def set_task_count(self, count):
        self.task_count = count
        self._refresh()

    def toggle_pause(self):
        self.paused = not self.paused
        self._refresh()
        self.pause_changed.emit(self.paused)

    def _refresh(self):
        if self.paused:
            self.status_action.setText("● Lilly is Paused")
            self.pause_action.setText("Resume Lilly")
            self.tray.setIcon(make_lilly_icon(False))
            base = "Lilly • Paused"
        else:
            self.status_action.setText("● Lilly is Active")
            self.pause_action.setText("Pause Lilly")
            self.tray.setIcon(make_lilly_icon(True))
            base = "Lilly • Active"

        if self.watched_title:
            short = self.watched_title[:45] + ("…" if len(self.watched_title) > 45 else "")
            self.watch_action.setText(f"Chrome: Watching {short}")
            self.tray.setToolTip(f"{base} • Watching Chrome")
        else:
            self.watch_action.setText("Chrome: No tab selected")
            self.tray.setToolTip(base)

        self.capture_action.setText(
            f"Capture: {self.last_capture}" if self.last_capture
            else ("Capture: Waiting for first image" if self.watched_title else "Capture: Waiting")
        )
        self.tasks_action.setText(f"Tasks: {self.task_count} active")
