import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from .notifications import LillyAlert

_active_alerts = []

def show_alert(title: str, message: str):
    alert = LillyAlert(title, message)
    _active_alerts.append(alert)
    alert.closed.connect(lambda: _active_alerts.remove(alert) if alert in _active_alerts else None)
    alert.show()

def run():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # V1 startup test: proves persistent popup + sound works.
    QTimer.singleShot(
        800,
        lambda: show_alert(
            "Lilly is active",
            "Persistent notifications are ready. This alert stays until you click Acknowledge."
        )
    )
    sys.exit(app.exec())
