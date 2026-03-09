import re
import unicodedata
import torch
torch.inference_mode = torch.no_grad
from config import WakeWordConfig
from config import TTSConfig

WAKE_WORD = WakeWordConfig.WORD
CHUNK_LIMIT = TTSConfig.CHUNK_LIMIT

def _produce_audio(parts, audio_queue, generate_audio):
    for part in parts:
        wav = generate_audio(part)
        audio_queue.put(wav)
    audio_queue.put(None)   

def _chunk_text(text: str):
    text = text.strip()
    parts = []
    while len(text) > CHUNK_LIMIT:
        cut = text.rfind(", ", 0, CHUNK_LIMIT)
        if cut == -1:
            cut = text.rfind(" ", 0, CHUNK_LIMIT)
        if cut == -1:
            cut = CHUNK_LIMIT
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


def _prepare_for_tts(text):
    text = text.strip()

    while re.search(r"(\d)\.(\d{3})\b", text):
        text = re.sub(r"(\d)\.(\d{3})\b", r"\1\2", text)

    text = re.sub(r"(?<!\.)\.(?!\.)", ",", text)

    text = re.sub(r"\s+([,!?;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def _normalize(text):
    text = text.strip().lower()
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )
    text = re.sub(r"\s+", " ", text)
    return text

def validate_transcript(text: str, wake_word: str = WAKE_WORD):
    if not text or not text.strip():
        print("[VALIDATION] EMPTY TEXT — IGNORING")
        return False, None
    
    normalized = _normalize(text)
    
    if WAKE_WORD is None:
        return True, normalized

    pattern = rf"^\s*\b{re.escape(wake_word)}\b[,:;\-–—]?\s*(.*)$"
    match = re.search(pattern, normalized)

    if not match:
        print(f"[VALIDATION] REJECTED TEXT — '{text}'")
        return False, None

    command = match.group(1).strip()
    return True, command