import torch
torch.inference_mode = torch.no_grad
import sounddevice as sd
from TTS.api import TTS
from benchmark import benchmark
import threading
import queue
import re

tts = None

def _chunk_text(text: str, limit: int = 180):
    text = text.strip()
    parts = []
    while len(text) > limit:
        cut = text.rfind(", ", 0, limit)
        if cut == -1:
            cut = text.rfind(" ", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts

def _select_device():
    try:
        import torch_directml
        print("[DEVICE] USING DIRECTML")
        return torch_directml.device()
    except ImportError:
        pass

    if torch.cuda.is_available():
        print("[DEVICE] USING CUDA")
        return torch.device("cuda")

    print("[DEVICE] USING CPU")
    return torch.device("cpu")


def _prepare_for_tts(text: str) -> str:
    text = text.strip()

    while re.search(r"(\d)\.(\d{3})\b", text):
        text = re.sub(r"(\d)\.(\d{3})\b", r"\1\2", text)

    text = re.sub(r"(?<!\.)\.(?!\.)", ",", text)

    text = re.sub(r"\s+([,!?;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

@benchmark
def init():
    global tts
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    device = _select_device()
    tts = TTS(model_name).to(device)

@benchmark
def generate_audio(answer):
    global tts
    wav = tts.tts(
        text=answer,
        speaker="Alma María",
        language="pt"
    )
    return wav

def play_audio(wav):  
    sd.play(wav, samplerate=22000)
    sd.wait()

def speak(answer):
    if not answer:
        return

    answer = _prepare_for_tts(answer)
    parts = _chunk_text(answer, limit=180)

    q = queue.Queue(maxsize=2)

    def producer():
        for part in parts:
            wav = generate_audio(part)
            q.put(wav)
        q.put(None)

    t = threading.Thread(target=producer, daemon=True)
    t.start()

    while True:
        wav = q.get()
        if wav is None:
            break
        play_audio(wav)