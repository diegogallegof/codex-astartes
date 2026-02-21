import os

raw = os.getenv("WATCHED_PATHS", "~/.ssh,~/.bashrc,~/.zshrc,~/.env,~/Documents")
WATCHED_PATHS = [os.path.expanduser(p.strip()) for p in raw.split(",")]
