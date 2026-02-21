# Codex Astartes — Shield of Macragge

> *"Our struggle is not against flesh and blood, but against the rulers, against the authorities, against the powers of this dark world."* — Ephesians 6:12

The sacred repository of the **Ultramarines Security Chapter** — a multi-agent defensive security system that watches over your machine in real time.

---

## The Chapter

| Agent | Role |
|---|---|
| **Calgar** | Orchestrator — commands all agents |
| **Torias** | Network watcher — monitors suspicious connections |
| **Cassius** | Process/malware hunter — hunts rogue processes |
| **Pythol** | System health monitor — CPU, RAM, Disk |
| **Tigurius** | File change sentinel — watches sacred paths |
| **Servitor** | Downloads folder guardian |

---

## Quick Start

```bash
git clone git@github.com:diegogallegof/codex-astartes.git
cd codex-astartes
git checkout -b world/<your-machine-name>
cp worlds/NEW_WORLD_TEMPLATE.env .env
# Fill in your ElevenLabs API key and thresholds
bash setup.sh
python main.py
```

---

## Branching Doctrine

- `main` — sacred core, shared logic only
- `world/<name>` — machine-specific configuration

---

*For His Word and His Glory.*
