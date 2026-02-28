# Codex Astartes — Shield of Macragge

> *"Our struggle is not against flesh and blood, but against the rulers, against the authorities, against the powers of this dark world."* — Ephesians 6:12

**Codex Astartes** is a personal, always-on defensive security system for macOS — built as a multi-agent Python framework, voiced by a custom cloned voice engine, and themed around the Warhammer 40,000 Ultramarines Chapter.

Every agent runs as a daemon thread, patrols a specific threat surface, and reports through a central orchestrator. When a threat is detected, the system speaks it aloud and writes it to a persistent log.

---

## The Chapter — Active Agents

| Agent | Lore Role | Security Function |
|---|---|---|
| **Calgar** | Chapter Master | Orchestrator — receives all threats and commands response |
| **Torias** | Scout Sergeant | Network watcher — monitors suspicious connections and ports |
| **Cassius** | Chaplain | Process/malware hunter — hunts rogue and suspicious processes |
| **Pythol** | Apothecary | System health monitor — CPU, RAM, and Disk thresholds |
| **Tigurius** | Chief Librarian | File sentinel — watches sacred paths for unauthorized changes |
| **Servitor** | Chapter Servitor | Downloads folder guardian — detects clutter, sorts files at EOD |
| **Sicarius** | Captain 2nd Company | LaunchAgent warden — detects new persistence entries in launchd |
| **Ventris** | Captain 4th Company | USB sentinel — alerts when external drives are mounted |

---

## Architecture

```
main.py
│
├── core/
│   ├── calgar.py       ← Orchestrator: enlists agents, deploys threads, routes threats
│   ├── threat.py       ← Threat dataclass: agent, description, severity, timestamp, metadata
│   ├── voice.py        ← Three-tier voice engine: ElevenLabs → XTTS clone → macOS say
│   ├── tts_engine.py   ← Standalone XTTS v2 runner (Python 3.11, called as subprocess)
│   └── logger.py       ← File logger: writes all threats to logs/chapter.log
│
├── agents/
│   ├── torias.py       ← Network connections monitor (psutil)
│   ├── cassius.py      ← Process scanner (psutil)
│   ├── pythol.py       ← CPU / RAM / Disk health (psutil)
│   ├── tigurius.py     ← File system watcher (watchdog)
│   ├── servitor.py     ← Downloads folder guardian (os + shutil)
│   ├── sicarius.py     ← LaunchAgent watcher (watchdog + plistlib)
│   └── ventris.py      ← USB / external volume monitor (psutil)
│
├── worlds/
│   ├── NEW_WORLD_TEMPLATE.env          ← Template for new machines
│   ├── com.codex.astartes.plist        ← launchd auto-start agent (macOS)
│   └── voice_reference.mp3             ← Voice clone reference audio (gitignored, machine-specific)
│
├── logs/
│   └── chapter.log     ← Local threat log (gitignored)
│
├── .env                ← Machine secrets (gitignored — never committed)
└── requirements.txt
```

### Threat Flow

```
Agent detects event
      ↓
calgar.report(Threat)
      ↓
  ┌───┴────────────────┐
  │ print to terminal  │
  │ log to chapter.log │
  │ speak via TTS      │
  └────────────────────┘
```

---

## Prerequisites

- macOS (tested on MacBook Pro M3, macOS Sequoia)
- Python 3.9+ (Chapter core) + Python 3.11 (XTTS voice engine)
- Homebrew
- `ffmpeg` (for audio playback)
- An ElevenLabs account (optional — system works fully offline without it)

```bash
brew install ffmpeg python@3.11
```

---

## Setup — Step by Step

### 1. Clone the repository

```bash
git clone https://github.com/diegogallegof/codex-astartes.git
cd codex-astartes
```

### 2. Create your world branch

Each machine gets its own branch. This keeps machine-specific config out of `main`.

```bash
git checkout -b world/<your-machine-name>
# Example: git checkout -b world/macragge
```

### 3. Create your virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure your environment

```bash
cp worlds/NEW_WORLD_TEMPLATE.env .env
```

Edit `.env` with your values (see **Configuration** section below). This file is gitignored — it will never be committed.

### 5. Set up the local voice engine (optional but recommended)

The Chapter can clone any voice locally using XTTS v2 — no API key or quota needed.

```bash
# Create the XTTS environment
python3.11 -m venv ~/.codex_astartes/.xtts_venv
~/.codex_astartes/.xtts_venv/bin/pip install TTS torch==2.5.1 torchaudio==2.5.1 transformers==4.44.2

# Place your voice reference audio (6-30 seconds of your target voice)
cp /path/to/your/voice_sample.mp3 worlds/voice_reference.mp3
```

The first time `tts_engine.py` runs it downloads the XTTS v2 model (~1.87GB) to `~/.codex_astartes/xtts_models/`.

### 6. Boot the Chapter

```bash
python main.py
```

Or to run detached from the terminal (survives terminal close):

```bash
python main.py > /tmp/codex-astartes.log 2>&1 &
disown
```

### 7. Auto-start at login (macOS)

Install the provided launchd plist so the Chapter deploys automatically every time the machine starts:

```bash
cp worlds/com.codex.astartes.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.codex.astartes.plist
```

**Important:** After installing the plist, grant Full Disk Access to the Python binary so agents like Servitor can access protected directories (Downloads, Documents, etc.):

1. Open `System Settings → Privacy & Security → Full Disk Access`
2. Click `+`
3. Press `⌘ ⇧ G` and paste:
   ```
   /path/to/your/codex-astartes/.venv/bin/python
   ```
4. Toggle it ON

Chapter output (when running via launchd) is written to `/tmp/codex-astartes.log`.

---

## Configuration — `.env` Reference

| Variable | Default | Description |
|---|---|---|
| `ELEVENLABS_API_KEY` | — | Your ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | — | Voice ID from your ElevenLabs account |
| `CPU_ALERT_PERCENT` | `85` | CPU usage % that triggers a Pythol alert |
| `RAM_ALERT_PERCENT` | `90` | RAM usage % that triggers a Pythol alert |
| `DISK_ALERT_PERCENT` | `95` | Disk usage % that triggers a Pythol alert |
| `PROCESS_POLL_INTERVAL` | `15` | Cassius scan interval (seconds) |
| `NETWORK_POLL_INTERVAL` | `10` | Torias scan interval (seconds) |
| `HEALTH_POLL_INTERVAL` | `20` | Pythol scan interval (seconds) |
| `DOWNLOADS_SCAN_INTERVAL_MINUTES` | `30` | Servitor patrol interval (minutes) |
| `DOWNLOADS_MAX_AGE_DAYS` | `30` | Age in days before a file is flagged as old |
| `DOWNLOADS_MAX_FILES` | `100` | Max items in Downloads before alert |
| `EOD_SORT_HOUR` | `20` | Hour (24h) when Servitor auto-sorts Downloads |
| `WATCHED_PATHS` | `~/.ssh,~/.zshrc,...` | Comma-separated paths for Tigurius to watch |
| `SUSPICIOUS_PORTS` | `4444,6666,31337,...` | Ports that trigger a Torias HIGH alert |
| `TRUSTED_IPS` | `127.0.0.1,...` | IPs excluded from Torias network alerts |

---

## Agents — Detailed Reference

### Calgar — Orchestrator (`core/calgar.py`)

The Chapter Master. All agents report to Calgar via `calgar.report(Threat)`. On every report, Calgar:
- Prints the threat to the terminal
- Writes it to `logs/chapter.log` via the logger
- Speaks it aloud via ElevenLabs TTS

Calgar runs each agent's `patrol()` method in a dedicated daemon thread.

---

### Torias — Network Watcher (`agents/torias.py`)

Monitors all active network connections using `psutil.net_connections()`. Flags any outbound connection to a port in `SUSPICIOUS_PORTS` that is not coming from a trusted IP or a trusted process.

**Trusted processes:** `symptomsd` (Apple diagnostics) — whitelisted to prevent false positives.

**Known fix:** On macOS, `psutil.net_connections()` raises `AccessDenied` for system-owned connections. Torias catches this silently at both the scan and per-connection level.

---

### Cassius — Process Hunter (`agents/cassius.py`)

Scans all running processes every `PROCESS_POLL_INTERVAL` seconds. Flags any process whose name matches known malware keywords:

```
xmrig, minerd, cryptominer, netcat, ncat, socat,
msfconsole, meterpreter, metasploit, backdoor, rootkit,
keylogger, mimikatz, cobalt strike
```

Maintains a `MACOS_ALLOWLIST` of legitimate macOS system processes to prevent false positives (e.g. `launchd`, `NotificationCenter`, `SiriNCService`).

---

### Pythol — Health Monitor (`agents/pythol.py`)

Polls CPU, RAM, and Disk usage every `HEALTH_POLL_INTERVAL` seconds. Reports:
- `HIGH` when CPU exceeds `CPU_ALERT_PERCENT`
- `HIGH` when RAM exceeds `RAM_ALERT_PERCENT`
- `HIGH` when Disk exceeds `DISK_ALERT_PERCENT`

---

### Tigurius — File Sentinel (`agents/tigurius.py`)

Uses the `watchdog` library to monitor `WATCHED_PATHS` for file system events (create, modify, delete). Events are batched into a **5-second window** to prevent spam when many files change at once (e.g. bulk deletions).

- Single file event → names the specific file
- Multiple files in the window → reports count (e.g. "12 files deleted")

Severities: `MEDIUM` for deletions/modifications, `LOW` for creations.

---

### Servitor — Downloads Guardian (`agents/servitor.py`)

Patrols `~/Downloads` every `DOWNLOADS_SCAN_INTERVAL_MINUTES`. Performs three checks each cycle:

1. **Loose file detection** — flags any file sitting directly in the Downloads root (not inside a category folder)
2. **Age check** — flags files not modified in the last `DOWNLOADS_MAX_AGE_DAYS` days
3. **Count check** — alerts if total items exceed `DOWNLOADS_MAX_FILES`

**End-of-day auto-sort:** At `EOD_SORT_HOUR` (default 20:00), Servitor automatically moves all loose files into category subfolders based on extension:

| Folder | Extensions |
|---|---|
| Images | png, jpg, jpeg, gif, webp, svg |
| Documents | pdf, docx, doc, pptx, ppt, txt |
| Data | csv, xlsx, xls, numbers, gz |
| Archives | zip |
| Videos | mp4, mov |
| Audio | wav, mp3 |
| Installers | dmg, pkg, apk |
| Web | html, htm |
| Dev | sqlite, ics, db, md |
| Misc | everything else |

System files (`.DS_Store`, `.localized`, `desktop.ini`) are permanently ignored.

**Permission note:** When running via launchd without Full Disk Access, Servitor prints a clear message and skips the patrol cycle rather than crashing.

---

### Sicarius — LaunchAgent Warden (`agents/sicarius.py`)

Watches launchd persistence directories for new `.plist` files using `watchdog`:

- `~/Library/LaunchAgents` — user-level auto-start entries
- `/Library/LaunchAgents` — system-wide user agents
- `/Library/LaunchDaemons` — system-wide daemons (requires root)

When a new `.plist` appears, Sicarius parses it with `plistlib` to extract the command it will execute, then reports `HIGH` severity via Calgar.

This is the #1 persistence vector for macOS malware — any program that wants to survive reboots must register here.

---

### Ventris — USB Sentinel (`agents/ventris.py`)

Polls `psutil.disk_partitions()` every 5 seconds. Any new mount point under `/Volumes/` triggers a `MEDIUM` severity alert with the volume name and mount path. Ejections are logged silently to the terminal.

---

## Voice Engine (`core/voice.py` + `core/tts_engine.py`)

The Chapter never goes silent. Voice alerts use a three-tier priority system:

```
1. ElevenLabs API   — fast (~4s), premium quality, requires quota
       ↓ (fails or quota exceeded)
2. XTTS v2 clone    — fully offline (~10s), cloned from voice_reference.mp3
       ↓ (fails or not configured)
3. macOS say        — instant, built-in robot voice, always available
```

### Tier 1 — ElevenLabs

- Model: `eleven_turbo_v2_5` (free tier compatible)
- Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in `.env`
- Automatically used when quota is available; skipped when exhausted

### Tier 2 — XTTS v2 Local Voice Clone

A fully offline neural TTS engine using [Coqui XTTS v2](https://github.com/coqui-ai/TTS). Clones any voice from a short reference audio sample — no API, no quota, no third party.

**Voice profile (C1 — Calgar):**
- `temperature=0.6` — controlled, deliberate cadence
- `repetition_penalty=11.0` — clean, no wandering
- Pitch shifted -3 semitones via ffmpeg for deep resonance
- Reference: `worlds/voice_reference.mp3` (gitignored, machine-specific)

**Infrastructure:**
- Python 3.11 venv at `~/.codex_astartes/.xtts_venv/`
- Model (~1.87GB) at `~/.codex_astartes/xtts_models/`
- Called as a subprocess by `voice.py` to avoid dependency conflicts with the main Chapter venv

**To set up:**
```bash
python3.11 -m venv ~/.codex_astartes/.xtts_venv
~/.codex_astartes/.xtts_venv/bin/pip install TTS torch==2.5.1 torchaudio==2.5.1 transformers==4.44.2
cp /path/to/your_voice_sample.mp3 worlds/voice_reference.mp3
```

### Tier 3 — macOS `say`

Built-in macOS TTS. No setup required. Used only when both ElevenLabs and XTTS are unavailable.

---

## Logging (`core/logger.py`)

All threats are written to `logs/chapter.log` in addition to terminal output and voice alerts. The log is gitignored — local only.

**Log format:**
```
2026-02-28 20:15:32 | HIGH    | [Sicarius] New LaunchAgent registered: 'com.example.plist' — Command: /usr/bin/curl ...
2026-02-28 20:16:01 | MEDIUM  | [Tigurius] File deleted: /Users/.../Documents/report.pdf
2026-02-28 20:16:45 | INFO    | [Servitor] Old file detected: archive.zip (last modified 2025-09-01)
```

Severity mapping: `LOW → INFO`, `MEDIUM → WARNING`, `HIGH → ERROR`, `CRITICAL → CRITICAL`

To monitor in real time:
```bash
tail -f logs/chapter.log
```

Or use the shell alias (if configured):
```bash
chapter-log
```

---

## Branching Doctrine

| Branch | Purpose |
|---|---|
| `main` | Sacred core — shared logic, no secrets, no machine-specific config |
| `world/<name>` | Per-machine branch — `.env` values, plist paths, local overrides |

All development happens on `world/<name>`. Changes are merged into `main` via PR to keep contribution history intact.

**Never commit to `main` directly. Never commit `.env` files.**

---

## Shell Aliases (optional)

Add to your `.zshrc`:

```bash
alias codex="cd ~/Projects/codex-astartes && source .venv/bin/activate"
alias deploy="python main.py > /tmp/codex-astartes.log 2>&1 & disown && echo 'Chapter deployed.'"
alias chapter-log="tail -f ~/Projects/codex-astartes/logs/chapter.log"
alias reload="source ~/.zshrc"
```

---

## Troubleshooting

### Voice not working
- ElevenLabs quota exhausted → Chapter auto-falls back to XTTS local clone (~10s delay)
- XTTS not set up → Chapter falls back to macOS `say` (instant)
- Confirm `ffmpeg` is installed: `which ffplay`
- Tigurius voice alerts have a ~5 second delay due to the batch window
- To check ElevenLabs quota: [elevenlabs.io/app/subscription](https://elevenlabs.io/app/subscription)

### XTTS voice not working
- Confirm `~/.codex_astartes/.xtts_venv/bin/python3.11` exists
- Confirm `worlds/voice_reference.mp3` exists (gitignored — must be placed manually)
- Confirm model is downloaded: `ls ~/.codex_astartes/xtts_models/tts/`
- First run downloads ~1.87GB — requires internet connection

### Servitor: Access denied to Downloads
- Grant Full Disk Access to the Python binary in `System Settings → Privacy & Security → Full Disk Access`

### Torias spamming errors
- Fixed in current version — `AccessDenied` from `psutil.net_connections()` is caught silently

### Chapter not auto-starting after reboot
- Confirm plist is loaded: `launchctl list | grep astartes`
- Check output: `cat /tmp/codex-astartes.log`
- Reload: `launchctl unload ~/Library/LaunchAgents/com.codex.astartes.plist && launchctl load ~/Library/LaunchAgents/com.codex.astartes.plist`

### Multiple Chapter instances running
- `pkill -f "main.py"` then reload via launchctl

---

## Requirements

```
psutil
watchdog
python-dotenv
elevenlabs
```

Install: `pip install -r requirements.txt`

---

*For His Word and His Glory. The Chapter stands eternal.*
