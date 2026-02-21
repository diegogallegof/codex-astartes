import os
import time
import psutil
from core.threat import Threat, Severity

KNOWN_HERETICS = [
    "cryptominer", "xmrig", "minerd", "coinhive",
    "nc", "netcat", "ncat", "socat",
    "metasploit", "msfconsole", "meterpreter",
    "backdoor", "rootkit", "keylogger",
]


class Cassius:
    """Process/malware hunter — scans for suspicious processes."""

    NAME = "Cassius"

    def __init__(self, calgar):
        self.calgar = calgar
        self.interval = int(os.getenv("PROCESS_POLL_INTERVAL", 15))
        self.seen = set()

    def patrol(self):
        print(f"[{self.NAME}] Process hunt active.")
        while True:
            try:
                for proc in psutil.process_iter(["pid", "name", "exe"]):
                    name = (proc.info["name"] or "").lower()
                    for heretic in KNOWN_HERETICS:
                        if heretic in name and proc.info["pid"] not in self.seen:
                            self.seen.add(proc.info["pid"])
                            self.calgar.report(Threat(
                                agent=self.NAME,
                                description=f"Suspicious process detected: {proc.info['name']} (PID {proc.info['pid']})",
                                severity=Severity.CRITICAL,
                                metadata={"pid": proc.info["pid"], "name": proc.info["name"]},
                            ))
            except Exception as e:
                print(f"[{self.NAME}] Error: {e}")
            time.sleep(self.interval)
