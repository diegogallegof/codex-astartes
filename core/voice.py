import os
from core.threat import Threat


def speak(threat: Threat):
    """ElevenLabs TTS engine — voice of the Chapter."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key or api_key == "your_key_here":
        print(f"[VOICE] {threat}")
        return

    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import play

        client = ElevenLabs(api_key=api_key)
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=str(threat),
            model_id="eleven_monolingual_v1",
        )
        play(audio)
    except Exception as e:
        print(f"[VOICE ERROR] {e} — falling back to print: {threat}")
