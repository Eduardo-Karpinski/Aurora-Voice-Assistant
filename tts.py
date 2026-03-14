import utils
import sounddevice as sd
from TTS.api import TTS
from benchmark import benchmark
import threading
import queue
from config import TTSConfig

tts = None
_stop_event = threading.Event()
_lock = threading.Lock()

@benchmark
def init():
    global tts
    model_name = TTSConfig.MODEL_NAME
    device = utils._select_device()
    tts = TTS(model_name).to(device)

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