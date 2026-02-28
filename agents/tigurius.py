import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.threat import Threat, Severity

BATCH_WINDOW_SECONDS = 5

# Paths containing these segments are noisy internals — never alert on them
IGNORED_SEGMENTS = {"/.git/", "/__pycache__/", "/.venv/"}


class TiguriusHandler(FileSystemEventHandler):
    def __init__(self, calgar):
        self.calgar = calgar
        self._deleted = []
        self._created = []
        self._modified = []
        self._lock = threading.Lock()
        self._timer = None

    def _schedule_flush(self):
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(BATCH_WINDOW_SECONDS, self._flush)
        self._timer.daemon = True
        self._timer.start()

    def _flush(self):
        with self._lock:
            deleted = list(self._deleted)
            created = list(self._created)
            modified = list(self._modified)
            self._deleted.clear()
            self._created.clear()
            self._modified.clear()

        if deleted:
            count = len(deleted)
            label = deleted[0] if count == 1 else f"{count} files"
            self.calgar.report(Threat(
                agent="Tigurius",
                description=f"{'File' if count == 1 else str(count) + ' files'} deleted: {label}",
                severity=Severity.MEDIUM,
                metadata={"paths": deleted, "count": count},
            ))

        if created:
            count = len(created)
            label = created[0] if count == 1 else f"{count} files"
            self.calgar.report(Threat(
                agent="Tigurius",
                description=f"{'File' if count == 1 else str(count) + ' files'} created: {label}",
                severity=Severity.LOW,
                metadata={"paths": created, "count": count},
            ))

        if modified:
            count = len(modified)
            label = modified[0] if count == 1 else f"{count} files"
            self.calgar.report(Threat(
                agent="Tigurius",
                description=f"{'File' if count == 1 else str(count) + ' files'} modified: {label}",
                severity=Severity.MEDIUM,
                metadata={"paths": modified, "count": count},
            ))

    def _ignored(self, path):
        return any(seg in path for seg in IGNORED_SEGMENTS)

    def on_modified(self, event):
        if not event.is_directory and not self._ignored(event.src_path):
            with self._lock:
                self._modified.append(event.src_path)
            self._schedule_flush()

    def on_created(self, event):
        if not event.is_directory and not self._ignored(event.src_path):
            with self._lock:
                self._created.append(event.src_path)
            self._schedule_flush()

    def on_deleted(self, event):
        if not self._ignored(event.src_path):
            with self._lock:
                self._deleted.append(event.src_path)
            self._schedule_flush()


class Tigurius:
    """File change sentinel — watches sacred paths for unauthorized changes."""

    NAME = "Tigurius"

    def __init__(self, calgar):
        self.calgar = calgar
        raw = os.getenv("WATCHED_PATHS", "~/.ssh,~/.zshrc,~/.env,~/Documents")
        self.paths = [os.path.expanduser(p.strip()) for p in raw.split(",")]

    def patrol(self):
        print(f"[{self.NAME}] File sentinel active. Watching: {self.paths}")
        observer = Observer()
        handler = TiguriusHandler(self.calgar)
        for path in self.paths:
            if os.path.exists(path):
                observer.schedule(handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except Exception:
            observer.stop()
        observer.join()
