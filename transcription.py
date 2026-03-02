from faster_whisper import WhisperModel
import numpy as np
from benchmark import benchmark

MODEL_SIZE = "medium"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

LANGUAGE = "pt"
BEAM_SIZE = 1
VAD_FILTER = False
TEMPERATURE = 0
CONDITION_ON_PREVIOUS_TEXT = False

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
        #beam_size=BEAM_SIZE,
        language=LANGUAGE,
        vad_filter=VAD_FILTER,
        temperature=TEMPERATURE,
        condition_on_previous_text=CONDITION_ON_PREVIOUS_TEXT,
    )

    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text