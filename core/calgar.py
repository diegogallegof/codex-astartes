import threading
from core.threat import Threat
from core.voice import speak
from core.logger import log_threat, log_event


class Calgar:
    """Orchestrator — commands all agents of the Chapter."""

    def __init__(self):
        self.agents = []
        self._threads = []
        self._voice_lock = threading.Lock()

    def enlist(self, agent):
        self.agents.append(agent)

    def _speak_safe(self, threat):
        """Speak a threat aloud — skipped if voice is already busy."""
        if self._voice_lock.acquire(blocking=False):
            try:
                speak(threat)
            finally:
                self._voice_lock.release()

    def report(self, threat: Threat):
        print(f"[CALGAR] Threat received: {threat}")
        log_threat(threat)
        threading.Thread(target=self._speak_safe, args=(threat,), daemon=True).start()

    def deploy(self):
        print("[CALGAR] All units — deploy!")
        log_event("Chapter deployed — all agents on station.")
        for agent in self.agents:
            t = threading.Thread(target=agent.patrol, daemon=True)
            t.start()
            self._threads.append(t)

    def stand_by(self):
        try:
            for t in self._threads:
                t.join()
        except KeyboardInterrupt:
            print("\n[CALGAR] Chapter standing down. For His Glory.")
            log_event("Chapter standing down.")
