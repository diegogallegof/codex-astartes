import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.threat import Threat, Severity


class TiguriusHandler(FileSystemEventHandler):
    def __init__(self, calgar):
        self.calgar = calgar

    def on_modified(self, event):
        if not event.is_directory:
            self.calgar.report(Threat(
                agent="Tigurius",
                description=f"File modified: {event.src_path}",
                severity=Severity.MEDIUM,
                metadata={"path": event.src_path},
            ))

    def on_created(self, event):
        if not event.is_directory:
            self.calgar.report(Threat(
                agent="Tigurius",
                description=f"New file created: {event.src_path}",
                severity=Severity.LOW,
                metadata={"path": event.src_path},
            ))

    def on_deleted(self, event):
        self.calgar.report(Threat(
            agent="Tigurius",
            description=f"File deleted: {event.src_path}",
            severity=Severity.MEDIUM,
            metadata={"path": event.src_path},
        ))


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
