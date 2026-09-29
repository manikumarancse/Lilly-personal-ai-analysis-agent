import json
import threading
import uuid
from datetime import datetime
from pathlib import Path


class TaskEngine:
    SUPPORTED = {"price_above", "price_below"}

    def __init__(self, data_dir="data"):
        self.path = Path(data_dir) / "tasks.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._tasks = []
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self._tasks = data
        except (json.JSONDecodeError, OSError):
            self._tasks = []

    def _save(self):
        self.path.write_text(json.dumps(self._tasks, indent=2), encoding="utf-8")

    def list_tasks(self):
        with self._lock:
            return [dict(task) for task in self._tasks]

    def add_task(self, kind, level, label=""):
        if kind not in self.SUPPORTED:
            raise ValueError("Unsupported task type")
        level = float(level)
        task = {
            "id": uuid.uuid4().hex[:10],
            "kind": kind,
            "level": level,
            "label": str(label or "")[:160],
            "active": True,
            "triggered": False,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "triggered_at": None,
            "last_value": None,
        }
        with self._lock:
            self._tasks.append(task)
            self._save()
        return dict(task)

    def delete_task(self, task_id):
        with self._lock:
            before = len(self._tasks)
            self._tasks = [t for t in self._tasks if t.get("id") != task_id]
            changed = len(self._tasks) != before
            if changed:
                self._save()
            return changed

    def evaluate_price(self, value):
        value = float(value)
        now = datetime.now().isoformat(timespec="seconds")
        triggered = []
        with self._lock:
            for task in self._tasks:
                if not task.get("active") or task.get("triggered"):
                    continue
                task["last_value"] = value
                hit = (
                    task["kind"] == "price_above" and value >= float(task["level"])
                ) or (
                    task["kind"] == "price_below" and value <= float(task["level"])
                )
                if hit:
                    task["triggered"] = True
                    task["active"] = False
                    task["triggered_at"] = now
                    triggered.append(dict(task))
            self._save()
        return triggered
