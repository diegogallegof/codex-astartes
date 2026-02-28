import os
import shutil
import time
from datetime import datetime, timedelta
from core.threat import Threat, Severity
from core.voice import speak

# System files that are allowed to sit in root — never touch these
DOWNLOADS_IGNORED = {".ds_store", ".localized", "desktop.ini"}

# Extension → category folder mapping
EXT_TO_FOLDER = {
    # Images
    "png": "Images", "jpg": "Images", "jpeg": "Images",
    "gif": "Images", "webp": "Images", "svg": "Images",
    # Data
    "csv": "Data", "xlsx": "Data", "xls": "Data",
    "numbers": "Data", "gz": "Data",
    # Documents
    "pdf": "Documents", "docx": "Documents", "doc": "Documents",
    "pptx": "Documents", "ppt": "Documents", "txt": "Documents",
    # Archives
    "zip": "Archives",
    # Videos
    "mp4": "Videos", "mov": "Videos",
    # Audio
    "wav": "Audio", "mp3": "Audio",
    # Installers
    "dmg": "Installers", "pkg": "Installers", "apk": "Installers",
    # Web
    "html": "Web", "htm": "Web",
    # Dev
    "sqlite": "Dev", "ics": "Dev", "db": "Dev", "md": "Dev",
}


class Servitor:
    """Downloads folder guardian — monitors for anomalies, clutter, and auto-sorts at end of day."""

    NAME = "Servitor"

    def __init__(self, calgar):
        self.calgar = calgar
        self.interval = int(os.getenv("DOWNLOADS_SCAN_INTERVAL_MINUTES", 30)) * 60
        self.max_age_days = int(os.getenv("DOWNLOADS_MAX_AGE_DAYS", 30))
        self.max_files = int(os.getenv("DOWNLOADS_MAX_FILES", 100))
        self.eod_hour = int(os.getenv("EOD_SORT_HOUR", 20))  # default 8 PM
        self.downloads_path = os.path.expanduser("~/Downloads")
        self._reported_loose = set()
        self._last_sort_date = None

    def _check_loose_files(self):
        """Flag any files sitting directly in Downloads root."""
        for entry in os.listdir(self.downloads_path):
            if entry.lower() in DOWNLOADS_IGNORED:
                continue
            full_path = os.path.join(self.downloads_path, entry)
            if os.path.isfile(full_path) and full_path not in self._reported_loose:
                self._reported_loose.add(full_path)
                self.calgar.report(Threat(
                    agent=self.NAME,
                    description=f"Loose file detected in Downloads root: '{entry}' — must be moved to a proper folder",
                    severity=Severity.LOW,
                    metadata={"path": full_path, "file": entry},
                ))

    def _resolve_folder(self, filename):
        """Return the target folder for a file based on its extension."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return EXT_TO_FOLDER.get(ext, "Misc")

    def _auto_sort(self):
        """End-of-day routine — move all loose files into their proper category folders."""
        moved = []
        errors = []

        for entry in os.listdir(self.downloads_path):
            if entry.lower() in DOWNLOADS_IGNORED:
                continue
            full_path = os.path.join(self.downloads_path, entry)
            if not os.path.isfile(full_path):
                continue

            target_folder = self._resolve_folder(entry)
            target_dir = os.path.join(self.downloads_path, target_folder)
            os.makedirs(target_dir, exist_ok=True)

            target_path = os.path.join(target_dir, entry)
            # Avoid overwriting — rename if conflict
            if os.path.exists(target_path):
                base, ext = os.path.splitext(entry)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                target_path = os.path.join(target_dir, f"{base}_{timestamp}{ext}")

            try:
                shutil.move(full_path, target_path)
                moved.append(f"{entry} → {target_folder}/")
                self._reported_loose.discard(full_path)
            except Exception as e:
                errors.append(f"{entry}: {e}")

        if moved:
            summary = f"{len(moved)} file{'s' if len(moved) > 1 else ''} sorted into category folders"
            print(f"[{self.NAME}] End-of-day sort complete: {summary}")
            for m in moved:
                print(f"  {m}")
            self.calgar.report(Threat(
                agent=self.NAME,
                description=f"End-of-day auto-sort complete: {summary}",
                severity=Severity.LOW,
                metadata={"moved": moved, "count": len(moved)},
            ))
            speak(f"End of day sort complete. {len(moved)} files have been classified and secured.")
        else:
            print(f"[{self.NAME}] End-of-day sort: sector already clean.")
            speak("End of day sort complete. Downloads sector was already clean.")

        if errors:
            print(f"[{self.NAME}] Sort errors: {errors}")

    def _should_sort_today(self):
        """Returns True if end-of-day sort should run now."""
        now = datetime.now()
        return (
            now.hour >= self.eod_hour
            and self._last_sort_date != now.date()
        )

    def patrol(self):
        print(f"[{self.NAME}] Downloads guardian active. End-of-day sort at {self.eod_hour:02d}:00.")
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

                self._check_loose_files()

                if self._should_sort_today():
                    self._last_sort_date = datetime.now().date()
                    self._auto_sort()

                cutoff = datetime.now() - timedelta(days=self.max_age_days)
                for entry in entries:
                    if entry.lower() in DOWNLOADS_IGNORED:
                        continue
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

                speak("Servitor patrol complete. Downloads sector secured.")
                print(f"[{self.NAME}] Patrol complete. Sector secured.")
            except Exception as e:
                print(f"[{self.NAME}] Error: {e}")
            time.sleep(self.interval)
