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
    painter.setPen(QColor("#FFFFFF"))
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
        self.tray = QSystemTrayIcon(make_lilly_icon(True), parent)
        self.tray.setToolTip("Lilly • Active")
        menu = QMenu()
        self.status_action = QAction("● Lilly is Active")
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        menu.addSeparator()
        test_action = QAction("Test persistent alert")
        test_action.triggered.connect(self.test_alert.emit)
        menu.addAction(test_action)
        status_action = QAction("Show Lilly status")
        status_action.triggered.connect(self.status_requested.emit)
        menu.addAction(status_action)
        self.pause_action = QAction("Pause Lilly")
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)
        menu.addSeparator()
        exit_action = QAction("Exit Lilly")
        exit_action.triggered.connect(self.exit_requested.emit)
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)

    def show(self):
        self.tray.show()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.status_action.setText("● Lilly is Paused")
            self.pause_action.setText("Resume Lilly")
            self.tray.setToolTip("Lilly • Paused")
            self.tray.setIcon(make_lilly_icon(False))
        else:
            self.status_action.setText("● Lilly is Active")
            self.pause_action.setText("Pause Lilly")
            self.tray.setToolTip("Lilly • Active")
            self.tray.setIcon(make_lilly_icon(True))
        self.pause_changed.emit(self.paused)
