import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("COQUI_TOS_AGREED", "1")
os.environ.setdefault("MIOPEN_LOG_LEVEL", "3")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import soundfile as sf
import tts
from config import TTSConfig

# python tests/test_tts.py Olá, isto é um teste de voz.
texto = " ".join(sys.argv[1:]).strip() or "Olá, isto é um teste de voz."
tts.init()
wav = tts.generate_audio(texto)
destino = Path(__file__).resolve().parent / "out" / "tts.wav"
destino.parent.mkdir(exist_ok=True)
sf.write(destino, wav, TTSConfig.SAMPLE_RATE)
print(destino)
tts.play_audio(wav)
