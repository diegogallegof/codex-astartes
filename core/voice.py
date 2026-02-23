import os
from dotenv import load_dotenv
from core.threat import Threat

load_dotenv()


def speak(message):
    """ElevenLabs TTS engine — voice of the Chapter. Accepts a Threat or a plain string."""
    text = str(message)
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key or api_key == "your_key_here":
        print(f"[VOICE] {text}")
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
    except Exception as e:
        print(f"[VOICE ERROR] {e} — falling back to print: {text}")
