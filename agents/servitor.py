import os
import time
from datetime import datetime, timedelta
from core.threat import Threat, Severity


class Servitor:
    """Downloads folder guardian — monitors for anomalies and old clutter."""

    NAME = "Servitor"

    def __init__(self, calgar):
        self.calgar = calgar
        self.interval = int(os.getenv("DOWNLOADS_SCAN_INTERVAL_MINUTES", 30)) * 60
        self.max_age_days = int(os.getenv("DOWNLOADS_MAX_AGE_DAYS", 30))
        self.max_files = int(os.getenv("DOWNLOADS_MAX_FILES", 100))
        self.downloads_path = os.path.expanduser("~/Downloads")

    def patrol(self):
        print(f"[{self.NAME}] Downloads guardian active.")
        while True:
            try:
                entries = os.listdir(self.downloads_path)
                file_count = len(entries)

                if file_count > self.max_files:
                    self.calgar.report(Threat(
                        agent=self.NAME,
                        description=f"Downloads folder has {file_count} items (max: {self.max_files})",
                        severity=Severity.LOW,
                        metadata={"count": file_count},
                    ))

                cutoff = datetime.now() - timedelta(days=self.max_age_days)
                for entry in entries:
                    full_path = os.path.join(self.downloads_path, entry)
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                        if mtime < cutoff:
                            self.calgar.report(Threat(
                                agent=self.NAME,
                                description=f"Old file detected: {entry} (last modified {mtime.date()})",
                                severity=Severity.LOW,
                                metadata={"path": full_path, "age_days": (datetime.now() - mtime).days},
                            ))
                    except Exception:
                        pass
            except Exception as e:
                print(f"[{self.NAME}] Error: {e}")
            time.sleep(self.interval)
