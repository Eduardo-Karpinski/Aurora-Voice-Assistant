import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("COQUI_TOS_AGREED", "1")
os.environ.setdefault("MIOPEN_LOG_LEVEL", "3")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import soundfile as sf

import aurora.audio.tts as tts
from aurora.config import TTSConfig

# Sample spoken text. The voice follows the language of the text.
# python scripts/try_tts.py Olá, isto é um teste de voz.
text = " ".join(sys.argv[1:]).strip() or "Olá, isto é um teste de voz."
tts.init()
wav = tts.generate_audio(text)
destination = Path(__file__).resolve().parents[1] / "tests" / "out" / "tts.wav"
destination.parent.mkdir(exist_ok=True)
sf.write(destination, wav, TTSConfig.SAMPLE_RATE)
print(destination)
tts.play_audio(wav)
