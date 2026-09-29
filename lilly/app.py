import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from .chrome_bridge import ChromeBridge
from .notifications import LillyAlert
from .tray import LillyTray


class LillyApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Lilly")
        self.app.setQuitOnLastWindowClosed(False)
        self.active_alerts = []
        self.paused = False
        self.watched_tab = None
        self.latest_capture = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("Windows system tray is not available.")

        self.tray = LillyTray(self.app)
        self.tray.test_alert.connect(self.test_alert)
        self.tray.status_requested.connect(self.show_status)
        self.tray.pause_changed.connect(self.set_paused)
        self.tray.exit_requested.connect(self.shutdown)
        self.tray.show()

        self.bridge = ChromeBridge(parent=self.app)
        self.bridge.watch_started.connect(self.on_watch_started)
        self.bridge.watch_stopped.connect(self.on_watch_stopped)
        self.bridge.capture_received.connect(self.on_capture_received)
        self.bridge.bridge_error.connect(self.on_bridge_error)
        if not self.bridge.start():
            self.show_alert(
                "Lilly — Chrome Bridge Error",
                "Lilly could not start the Chrome connection on 127.0.0.1:8765. "
                "Another Lilly process may already be running.",
                force=True,
            )

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
            force=True,
        )

    def show_status(self):
        state = "PAUSED" if self.paused else "ACTIVE"
        if self.watched_tab:
            chrome = f'Watching: {self.watched_tab.get("title", "Untitled tab")}.'
        else:
            chrome = "No Chrome tab is currently selected."
        if self.latest_capture:
            capture = f' Latest chart capture: {self.latest_capture.get("captured_at")}.'
        else:
            capture = " No chart capture received yet."
        self.show_alert("Lilly — Status", f"Lilly is {state}. {chrome}{capture}", force=True)

    def set_paused(self, paused):
        self.paused = paused

    def on_watch_started(self, tab):
        self.watched_tab = tab
        self.latest_capture = None
        self.tray.set_watched_tab(tab.get("title"))
        self.show_alert(
            "Lilly — Chrome Connected",
            f'Now watching: {tab.get("title", "Untitled tab")}\n\n'
            "Visible chart capture is ready. Keep the selected chart tab visible when capturing.",
            force=True,
        )

    def on_watch_stopped(self):
        old_title = self.watched_tab.get("title") if self.watched_tab else "Chrome tab"
        self.watched_tab = None
        self.latest_capture = None
        self.tray.set_watched_tab(None)
        self.show_alert("Lilly — Chrome Watch Stopped", f"Stopped watching: {old_title}", force=True)

    def on_capture_received(self, meta):
        self.latest_capture = meta
        display_time = meta.get("captured_at", "").replace("T", " ")
        self.tray.set_last_capture(display_time)

    def on_bridge_error(self, error):
        self.show_alert("Lilly — Chrome Bridge Error", error, force=True)

    def shutdown(self):
        self.bridge.stop()
        for alert in list(self.active_alerts):
            alert.close()
        self.tray.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()


def run():
    lilly = LillyApplication()
    sys.exit(lilly.run())
