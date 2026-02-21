import os
import time
import psutil
from core.threat import Threat, Severity


class Pythol:
    """System health monitor — CPU, RAM, Disk."""

    NAME = "Pythol"

    def __init__(self, calgar):
        self.calgar = calgar
        self.interval = int(os.getenv("HEALTH_POLL_INTERVAL", 20))
        self.cpu_threshold = float(os.getenv("CPU_ALERT_PERCENT", 85))
        self.ram_threshold = float(os.getenv("RAM_ALERT_PERCENT", 90))
        self.disk_threshold = float(os.getenv("DISK_ALERT_PERCENT", 95))

    def patrol(self):
        print(f"[{self.NAME}] Health monitor active.")
        while True:
            try:
                cpu = psutil.cpu_percent(interval=2)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage("/").percent

                if cpu >= self.cpu_threshold:
                    self.calgar.report(Threat(
                        agent=self.NAME,
                        description=f"CPU critical: {cpu}%",
                        severity=Severity.HIGH,
                        metadata={"cpu_percent": cpu},
                    ))
                if ram >= self.ram_threshold:
                    self.calgar.report(Threat(
                        agent=self.NAME,
                        description=f"RAM critical: {ram}%",
                        severity=Severity.HIGH,
                        metadata={"ram_percent": ram},
                    ))
                if disk >= self.disk_threshold:
                    self.calgar.report(Threat(
                        agent=self.NAME,
                        description=f"Disk critical: {disk}%",
                        severity=Severity.MEDIUM,
                        metadata={"disk_percent": disk},
                    ))
            except Exception as e:
                print(f"[{self.NAME}] Error: {e}")
            time.sleep(self.interval)
