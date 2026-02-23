import os
import time
import psutil
from core.threat import Threat, Severity

# Trusted system processes — never flag connections from these
TRUSTED_PROCESSES = {
    "symptomsd",        # Apple diagnostics and health telemetry daemon
}


class Torias:
    """Network watcher — monitors suspicious connections and ports."""

    NAME = "Torias"

    def __init__(self, calgar):
        self.calgar = calgar
        self.interval = int(os.getenv("NETWORK_POLL_INTERVAL", 10))
        self.suspicious_ports = [
            int(p) for p in os.getenv("SUSPICIOUS_PORTS", "4444,6666,31337,1337,9001").split(",")
        ]
        self.trusted_ips = os.getenv("TRUSTED_IPS", "127.0.0.1,192.168.1.1").split(",")

    def _process_name(self, pid):
        """Resolve PID to process name safely."""
        try:
            return psutil.Process(pid).name().lower() if pid else None
        except Exception:
            return None

    def patrol(self):
        print(f"[{self.NAME}] Network watch active.")
        while True:
            try:
                connections = psutil.net_connections(kind="inet")
                for conn in connections:
                    if conn.raddr:
                        port = conn.raddr.port
                        ip = conn.raddr.ip
                        if port in self.suspicious_ports and ip not in self.trusted_ips:
                            proc_name = self._process_name(conn.pid)
                            if proc_name in TRUSTED_PROCESSES:
                                continue
                            self.calgar.report(Threat(
                                agent=self.NAME,
                                description=f"Suspicious connection to {ip}:{port}"
                                            + (f" by {proc_name}" if proc_name else ""),
                                severity=Severity.HIGH,
                                metadata={"ip": ip, "port": port, "status": conn.status, "process": proc_name},
                            ))
            except Exception as e:
                print(f"[{self.NAME}] Error: {e}")
            time.sleep(self.interval)
