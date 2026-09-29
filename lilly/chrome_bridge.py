import base64
import json
import threading
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from PySide6.QtCore import QObject, Signal


class ChromeBridge(QObject):
    watch_started = Signal(dict)
    watch_stopped = Signal()
    capture_received = Signal(dict)
    bridge_error = Signal(str)

    def __init__(self, host="127.0.0.1", port=8765, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self._server = None
        self._thread = None
        self._watched_tab = None
        self._latest_capture = None
        self._lock = threading.Lock()
        self.capture_dir = Path("data") / "captures"
        self.capture_dir.mkdir(parents=True, exist_ok=True)

    @property
    def watched_tab(self):
        with self._lock:
            return dict(self._watched_tab) if self._watched_tab else None

    @property
    def latest_capture(self):
        with self._lock:
            return dict(self._latest_capture) if self._latest_capture else None

    def _save_capture(self, body):
        data_url = body.get("image_data", "")
        if not data_url.startswith("data:image/") or "," not in data_url:
            raise ValueError("Missing or invalid image_data")

        header, encoded = data_url.split(",", 1)
        extension = "png" if "png" in header else "jpg"
        image_bytes = base64.b64decode(encoded, validate=True)
        if len(image_bytes) > 15 * 1024 * 1024:
            raise ValueError("Capture is too large")

        now = datetime.now()
        filename = f"latest_chart.{extension}"
        image_path = self.capture_dir / filename
        image_path.write_bytes(image_bytes)

        meta = {
            "captured_at": now.isoformat(timespec="seconds"),
            "path": str(image_path.resolve()),
            "bytes": len(image_bytes),
            "tab_id": body.get("tab_id"),
            "title": str(body.get("title") or "Untitled tab")[:300],
            "url": str(body.get("url") or "")[:3000],
            "width": body.get("width"),
            "height": body.get("height"),
        }
        (self.capture_dir / "latest_chart.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
        with self._lock:
            self._latest_capture = meta
        self.capture_received.emit(meta)
        return meta

    def start(self):
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            def _headers(self, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()

            def _json(self, payload, status=200):
                self._headers(status)
                self.wfile.write(json.dumps(payload).encode("utf-8"))

            def do_OPTIONS(self):
                self._headers(204)

            def do_GET(self):
                if self.path == "/health":
                    self._json({
                        "ok": True,
                        "service": "lilly",
                        "version": "0.4.0",
                        "watching": bridge.watched_tab,
                        "latest_capture": bridge.latest_capture,
                    })
                elif self.path == "/watch":
                    self._json({"ok": True, "watching": bridge.watched_tab})
                elif self.path == "/capture/latest":
                    self._json({"ok": True, "capture": bridge.latest_capture})
                else:
                    self._json({"ok": False, "error": "Not found"}, 404)

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                try:
                    body = json.loads(self.rfile.read(length) or b"{}")
                except json.JSONDecodeError:
                    self._json({"ok": False, "error": "Invalid JSON"}, 400)
                    return

                if self.path == "/watch":
                    tab = {
                        "tab_id": body.get("tab_id"),
                        "title": str(body.get("title") or "Untitled tab")[:300],
                        "url": str(body.get("url") or "")[:3000],
                    }
                    with bridge._lock:
                        bridge._watched_tab = tab
                    bridge.watch_started.emit(tab)
                    self._json({"ok": True, "watching": tab})
                elif self.path == "/stop":
                    with bridge._lock:
                        bridge._watched_tab = None
                    bridge.watch_stopped.emit()
                    self._json({"ok": True, "watching": None})
                elif self.path == "/capture":
                    watched = bridge.watched_tab
                    if not watched:
                        self._json({"ok": False, "error": "No tab is being watched"}, 409)
                        return
                    if body.get("tab_id") != watched.get("tab_id"):
                        self._json({"ok": False, "error": "Capture is not from the selected tab"}, 403)
                        return
                    try:
                        meta = bridge._save_capture(body)
                    except (ValueError, TypeError, base64.binascii.Error) as exc:
                        self._json({"ok": False, "error": str(exc)}, 400)
                        return
                    self._json({"ok": True, "capture": meta})
                else:
                    self._json({"ok": False, "error": "Not found"}, 404)

            def log_message(self, format, *args):
                return

        try:
            self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        except OSError as exc:
            self.bridge_error.emit(str(exc))
            return False

        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="LillyChromeBridge",
            daemon=True,
        )
        self._thread.start()
        return True

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        self._thread = None
