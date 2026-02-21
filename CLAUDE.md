# Codex Astartes — Claude Code Instructions

## Project Overview
This is the Ultramarines Security Chapter — a multi-agent defensive security system for macOS.

## Structure
- `core/` — Orchestrator (Calgar), Voice engine, Threat dataclass
- `agents/` — Individual security agents (Torias, Cassius, Pythol, Tigurius, Servitor)
- `config/` — Thresholds and watched paths
- `worlds/` — Per-machine environment configs
- `logs/` — Local only, gitignored

## Branching Doctrine
- `main` — shared core only, never commit `.env`
- `world/<name>` — machine-specific config and overrides

## Running
```bash
cp worlds/NEW_WORLD_TEMPLATE.env .env   # fill in your keys
bash setup.sh
python main.py
```

## Never commit
- `.env` files with real keys
- `logs/` contents
- `audio_cache/`
