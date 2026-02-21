import threading
from core.threat import Threat
from core.voice import speak


class Calgar:
    """Orchestrator — commands all agents of the Chapter."""

    def __init__(self):
        self.agents = []
        self._threads = []

    def enlist(self, agent):
        self.agents.append(agent)

    def report(self, threat: Threat):
        print(f"[CALGAR] Threat received: {threat}")
        speak(threat)

    def deploy(self):
        print("[CALGAR] All units — deploy!")
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
