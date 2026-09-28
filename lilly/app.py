import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from .notifications import LillyAlert
from .tray import LillyTray

class LillyApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Lilly")
        self.app.setQuitOnLastWindowClosed(False)
        self.active_alerts = []
        self.paused = False

        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("Windows system tray is not available.")

        self.tray = LillyTray(self.app)
        self.tray.test_alert.connect(self.test_alert)
        self.tray.status_requested.connect(self.show_status)
        self.tray.pause_changed.connect(self.set_paused)
        self.tray.exit_requested.connect(self.shutdown)
        self.tray.show()

    def show_alert(self, title, message, force=False):
        if self.paused and not force:
            return
        alert = LillyAlert(title, message)
        self.active_alerts.append(alert)
        def remove_alert():
            if alert in self.active_alerts:
                self.active_alerts.remove(alert)
        alert.closed.connect(remove_alert)
        alert.show()

    def test_alert(self):
        self.show_alert(
            "Lilly — Test Alert",
            "Background mode is working. This alert remains visible until you acknowledge it.",
            force=True
        )

    def show_status(self):
        state = "PAUSED" if self.paused else "ACTIVE"
        self.show_alert(
            "Lilly — Status",
            f"Lilly is {state} and running in the Windows background. Chrome monitoring will be connected in Step 3.",
            force=True
        )

    def set_paused(self, paused):
        self.paused = paused

    def shutdown(self):
        for alert in list(self.active_alerts):
            alert.close()
        self.tray.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()

def run():
    lilly = LillyApplication()
    sys.exit(lilly.run())
