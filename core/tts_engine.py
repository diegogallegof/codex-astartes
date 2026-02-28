#!/usr/bin/env python3
"""
Standalone XTTS v2 voice engine — runs under Python 3.11 venv.
Called as a subprocess by voice.py. Reads text from argv, generates
cloned speech using the Calgar reference audio, and plays it.

Parameters locked to C1 profile:
  temperature=0.6, repetition_penalty=11.0, top_k=40, top_p=0.80
  pitch shift: asetrate * 0.85, atempo 1.176 (≈ -3 semitones)
"""

import os
import sys
import warnings
import subprocess
import tempfile

warnings.filterwarnings("ignore")
os.environ["COQUI_TOS_AGREED"] = "1"

MODEL_DIR = os.path.expanduser(
    "~/.codex_astartes/xtts_models/tts/tts_models--multilingual--multi-dataset--xtts_v2"
)
REFERENCE_AUDIO = os.path.join(
    os.path.dirname(__file__), "..", "worlds", "voice_reference.mp3"
)


def main():
    if len(sys.argv) < 2:
        print("[TTS ENGINE] No text provided.", file=sys.stderr)
        sys.exit(1)

    text = " ".join(sys.argv[1:])

    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    import torch
    import torchaudio

    config = XttsConfig()
    config.load_json(os.path.join(MODEL_DIR, "config.json"))
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=MODEL_DIR, eval=True)

    ref = os.path.abspath(REFERENCE_AUDIO)
    gpt_cond, speaker = model.get_conditioning_latents(audio_path=[ref])

    out = model.inference(
        text, "en", gpt_cond, speaker,
        temperature=0.6,
        repetition_penalty=11.0,
        top_k=40,
        top_p=0.80,
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw_f:
        raw_path = raw_f.name

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_f:
        out_path = out_f.name

    torchaudio.save(raw_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)

    # C1 pitch profile: -3 semitones down for deeper resonance
    subprocess.run(
        ["ffmpeg", "-i", raw_path,
         "-af", "asetrate=24000*0.85,aresample=24000,atempo=1.176",
         out_path, "-y"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    subprocess.run(
        ["ffplay", "-autoexit", "-nodisp", out_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    os.unlink(raw_path)
    os.unlink(out_path)


if __name__ == "__main__":
    main()
