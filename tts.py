import utils
import sounddevice as sd
from TTS.api import TTS
from benchmark import benchmark
import threading
import queue
import torch
from config import TTSConfig

tts = None
_stop_event = threading.Event()
_lock = threading.Lock()

@benchmark
def init():
    global tts
    print("[TTS] Baixando ou carregando o XTTS.", flush=True)
    # MIOpen re-tunes the vocoder for every audio length. That search takes
    # most of the synthesis time, so pick an algorithm directly.
    torch.backends.miopen.immediate = True
    model_name = TTSConfig.MODEL_NAME
    device = utils._select_device()
    tts = TTS(model_name).to(device)
    # SDPA on this ROCm stack raises hipErrorInvalidValue inside the XTTS GPT.
    tts.synthesizer.tts_model.gpt.gpt.config._attn_implementation = "eager"
    print("[TTS] Preparando a voz.", flush=True)
    tts.tts(text="Olá.", speaker=TTSConfig.SPEAKER, language=TTSConfig.LANGUAGE)

@benchmark
def generate_audio(answer):
    global tts
    wav = tts.tts(
        text=answer,
        speaker=TTSConfig.SPEAKER,
        language=TTSConfig.LANGUAGE
    )
    return wav

def play_audio(wav):  
    sd.play(wav, samplerate=TTSConfig.SAMPLE_RATE)
    sd.wait()

def stop():
    _stop_event.set()
    sd.stop()

def speak(answer):
    if not answer:
        return

    with _lock:
        _stop_event.clear()
        answer = utils._prepare_for_tts(answer)
        parts = utils._chunk_text(answer)
        audio_queue = queue.Queue(maxsize=2)

        threading.Thread(
            target=utils._produce_audio,
            args=(parts, audio_queue, generate_audio),
            daemon=True
        ).start()

        while True:
            if _stop_event.is_set():
                break
                
            try:
                wav = audio_queue.get(timeout=0.2)
                if wav is None:
                    break
                play_audio(wav)
            except queue.Empty:
                continue