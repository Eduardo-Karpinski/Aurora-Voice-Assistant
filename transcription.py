from faster_whisper import WhisperModel
import numpy as np
from benchmark import benchmark
from config import TranscriptionConfig

MODEL_SIZE = TranscriptionConfig.MODEL_SIZE
DEVICE = TranscriptionConfig.DEVICE
COMPUTE_TYPE = TranscriptionConfig.COMPUTE_TYPE
LANGUAGE = TranscriptionConfig.LANGUAGE
BEAM_SIZE = TranscriptionConfig.BEAM_SIZE
VAD_FILTER = TranscriptionConfig.VAD_FILTER
TEMPERATURE = TranscriptionConfig.TEMPERATURE
CONDITION_ON_PREVIOUS_TEXT = TranscriptionConfig.CONDITION_ON_PREVIOUS_TEXT

model = None

@benchmark
def init():
    global model
    model = WhisperModel(
        model_size_or_path=MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE
    )

@benchmark
def transcribe(audio: np.ndarray):
    global model
    segments, info = model.transcribe(
        audio,
        beam_size=BEAM_SIZE,
        language=LANGUAGE,
        vad_filter=VAD_FILTER,
        temperature=TEMPERATURE,
        condition_on_previous_text=CONDITION_ON_PREVIOUS_TEXT,
    )

    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text