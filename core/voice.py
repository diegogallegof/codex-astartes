import os
import subprocess
from dotenv import load_dotenv
from core.threat import Threat

load_dotenv()


def _say(text):
    """Fallback — macOS built-in TTS via the say command."""
    subprocess.run(["say", text], check=False)


def speak(message):
    """ElevenLabs TTS engine — voice of the Chapter. Falls back to macOS say on failure."""
    text = str(message)
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key or api_key == "your_key_here":
        _say(text)
        return

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
    except Exception:
        _say(text)
