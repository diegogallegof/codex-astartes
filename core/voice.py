import os
import subprocess
from dotenv import load_dotenv
from core.threat import Threat

load_dotenv()

XTTS_PYTHON = os.path.expanduser("~/.codex_astartes/.xtts_venv/bin/python3.11")
XTTS_ENGINE = os.path.join(os.path.dirname(__file__), "tts_engine.py")
VOICE_REFERENCE = os.path.join(os.path.dirname(__file__), "..", "worlds", "voice_reference.mp3")


def _xtts(text):
    """Local XTTS v2 voice — cloned Calgar voice, runs fully offline."""
    if not os.path.exists(XTTS_PYTHON) or not os.path.exists(VOICE_REFERENCE):
        return False
    result = subprocess.run(
        [XTTS_PYTHON, XTTS_ENGINE, text],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _say(text):
    """Last resort — macOS built-in TTS."""
    subprocess.run(["say", text], check=False)


def speak(message):
    """
    Voice of the Chapter. Priority:
      1. ElevenLabs (premium, fast)
      2. XTTS v2 local clone (offline, ~10s)
      3. macOS say (instant, robot fallback)
    """
    text = str(message)
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key or api_key == "your_key_here":
        if not _xtts(text):
            _say(text)
        return

    played = False
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs.play import play

        client = ElevenLabs(api_key=api_key)
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_turbo_v2_5",
        )
        play(audio)
        played = True
    except Exception:
        pass

    if not played:
        if not _xtts(text):
            _say(text)
