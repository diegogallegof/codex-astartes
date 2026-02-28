import os
import time
import psutil
from core.threat import Threat, Severity


class Ventris:
    """USB sentinel — monitors for external drives being mounted or ejected."""

    NAME = "Ventris"

    def __init__(self, calgar):
        self.calgar = calgar
        self.interval = 5
        self._known_volumes = set()

    def _external_volumes(self):
        """Return set of currently mounted external volumes (macOS mounts under /Volumes/)."""
        return {
            p.mountpoint
            for p in psutil.disk_partitions()
            if p.mountpoint.startswith("/Volumes/")
        }

    def patrol(self):
        self._known_volumes = self._external_volumes()
        known_display = {os.path.basename(v) for v in self._known_volumes} or {"none"}
        print(f"[{self.NAME}] USB sentinel active. Known volumes: {known_display}")

        while True:
            try:
                current = self._external_volumes()
                mounted = current - self._known_volumes
                ejected = self._known_volumes - current

                for mountpoint in mounted:
                    name = os.path.basename(mountpoint)
                    self.calgar.report(Threat(
                        agent=self.NAME,
                        description=f"External volume mounted: '{name}' at {mountpoint}",
                        severity=Severity.MEDIUM,
                        metadata={"mountpoint": mountpoint, "name": name},
                    ))

                for mountpoint in ejected:
                    name = os.path.basename(mountpoint)
                    print(f"[{self.NAME}] Volume ejected: '{name}'")

                self._known_volumes = current
            except Exception as e:
                print(f"[{self.NAME}] Error: {e}")
            time.sleep(self.interval)
