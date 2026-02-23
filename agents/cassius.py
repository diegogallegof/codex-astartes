import os
import time
import psutil
from core.threat import Threat, Severity

# Exact or specific substrings only — no short ambiguous tokens
KNOWN_HERETICS = [
    "xmrig", "minerd", "cryptominer", "coinhive",
    "netcat", "ncat", "socat",
    "msfconsole", "meterpreter", "metasploit",
    "backdoor", "rootkit", "keylogger",
    "mimikatz", "cobalt strike", "cobaltstrike",
]

# Legitimate macOS system processes — never flag these
MACOS_ALLOWLIST = {
    "launchd", "launchservicesd", "notificationcenter", "usernotificationcenter",
    "siriservice", "sirincservice", "siriinferenced", "findersyncextension",
    "audioclocksyncd", "cmfsyncagent", "imklaunchagent", "avconferenced",
    "hostinferencepro", "intelligencecontextd", "intelligenceplatformd",
    "intelligenceplatformcomputeservice", "syncdefaultsd", "safaribuookmarksyncagent",
    "safaribookmarksyncagent", "mapssyncd", "generativeexperiencesd", "mdsync",
    "distnoted", "cfnetwork", "nsurlsessiond", "accountsd", "cloudd",
    "bird", "rapportd", "symptomsd", "triald", "dprivacyd",
}


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
                    if name in MACOS_ALLOWLIST:
                        continue
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
