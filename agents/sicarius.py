import os
import time
import plistlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.threat import Threat, Severity

# Directories where launchd persistence entries live
WATCHED_LAUNCH_PATHS = [
    "~/Library/LaunchAgents",       # user-level (no root needed)
    "/Library/LaunchAgents",        # system-wide user agents
    "/Library/LaunchDaemons",       # system-wide daemons (root)
]


class SicariusHandler(FileSystemEventHandler):
    def __init__(self, calgar):
        self.calgar = calgar

    def _parse_plist(self, path):
        """Extract the command a plist will execute."""
        try:
            with open(path, "rb") as f:
                plist = plistlib.load(f)
            args = plist.get("ProgramArguments") or (
                [plist.get("Program")] if plist.get("Program") else []
            )
            return " ".join(str(a) for a in args)
        except Exception:
            return None

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".plist"):
            return
        filename = os.path.basename(event.src_path)
        command = self._parse_plist(event.src_path)
        desc = f"New LaunchAgent registered: '{filename}'"
        if command:
            desc += f" — Command: {command}"
        self.calgar.report(Threat(
            agent="Sicarius",
            description=desc,
            severity=Severity.HIGH,
            metadata={"path": event.src_path, "file": filename, "command": command},
        ))


class Sicarius:
    """LaunchAgent warden — detects new persistence entries planted in launchd directories."""

    NAME = "Sicarius"

    def __init__(self, calgar):
        self.calgar = calgar
        self.paths = [os.path.expanduser(p) for p in WATCHED_LAUNCH_PATHS]

    def patrol(self):
        observer = Observer()
        handler = SicariusHandler(self.calgar)
        watched = []
        for path in self.paths:
            if os.path.exists(path):
                observer.schedule(handler, path, recursive=False)
                watched.append(path)

        if not watched:
            print(f"[{self.NAME}] No watchable LaunchAgent paths found.")
            return

        print(f"[{self.NAME}] LaunchAgent warden active. Watching: {watched}")
        observer.start()
        try:
            while True:
                time.sleep(1)
        except Exception:
            observer.stop()
        observer.join()
