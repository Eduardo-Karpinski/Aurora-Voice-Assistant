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
    print("[TTS] Downloading or loading XTTS.", flush=True)
    # MIOpen re-tunes the vocoder for every audio length. That search takes
    # most of the synthesis time, so pick an algorithm directly.
    torch.backends.miopen.immediate = True
    model_name = TTSConfig.MODEL_NAME
    device = utils._select_device()
    tts = TTS(model_name).to(device)
    # SDPA on this ROCm stack raises hipErrorInvalidValue inside the XTTS GPT.
    tts.synthesizer.tts_model.gpt.gpt.config._attn_implementation = "eager"
    print("[TTS] Preparing the voice.", flush=True)
    # Prime the voice. This audio is not played.
    tts.tts(text="Olá.", speaker=TTSConfig.SPEAKER, language="pt")

@benchmark
def generate_audio(answer, language=None):
    global tts
    if language is None:
        language = utils.speech_language(answer)
    wav = tts.tts(
        text=answer,
        speaker=TTSConfig.SPEAKER,
        language=language
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
        language = utils.speech_language(answer)
        print(f"[TTS] Speaking {language}.", flush=True)
        parts = utils._chunk_text(answer)
        audio_queue = queue.Queue(maxsize=2)

        def generate(part):
            return generate_audio(part, language)

        threading.Thread(
            target=utils._produce_audio,
            args=(parts, audio_queue, generate),
            daemon=True
        ).start()

        while True:
            if _stop_event.is_set():
                break
                
            try:
                wav = audio_queue.get(timeout=0.2)
                if wav is None:
                    break
                if isinstance(wav, Exception):
                    raise wav
                play_audio(wav)
            except queue.Empty:
                continue