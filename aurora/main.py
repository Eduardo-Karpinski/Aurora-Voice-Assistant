import os
import traceback

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
# Lets the first run download XTTS. The weights stay under the non-commercial CPML. See NOTICE.
os.environ.setdefault("COQUI_TOS_AGREED", "1")
# 3 = errors only. MIOpen warns while it rejects convolution solvers during XTTS tuning.
os.environ.setdefault("MIOPEN_LOG_LEVEL", "3")

import threading

import aurora.audio.recorder as recorder
import aurora.audio.transcription as transcription
import aurora.audio.tts as tts
import aurora.language.llm as llm
import aurora.utils as utils
from aurora.benchmark import benchmark
from aurora.config import LLMConfig
from aurora.state import State, StateManager


def prepare_model_path():
    path = LLMConfig.MODEL_PATH
    if not os.path.isabs(path):
        package_dir = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(package_dir)
        path = os.path.join(root, path)
    LLMConfig.MODEL_PATH = path
    if os.path.isfile(path):
        return True
    print(f"[WARNING] Model file not found: {path}")
    print("[WARNING] Put the GGUF file in that folder and start again.")
    return False


def _run_init(target, errors):
    try:
        target()
    except Exception as exc:
        errors.append(exc)
        print(f"[ERROR] {target.__name__}: {exc}", flush=True)


@benchmark
def init_models():
    errors = []
    print("[INIT] Loading Whisper and XTTS. The first run downloads XTTS.", flush=True)
    threads = [
        threading.Thread(target=_run_init, args=(transcription.init, errors), name="Transcription-Thread"),
        threading.Thread(target=_run_init, args=(tts.init, errors), name="TTS-Thread"),
        threading.Thread(target=_run_init, args=(llm.init, errors), name="LLM-Thread"),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return not errors


def turn(state):
    state.set(State.LISTENING)
    audio = recorder.record_until_silence(state)

    state.set(State.TRANSCRIBING)
    text = transcription.transcribe(audio)
    valid, clean_text = utils.validate_transcript(text)
    if not valid:
        state.set(State.IDLE)
        return

    state.set(State.THINKING)
    answer = llm.ask(clean_text)
    if not answer or "[STOP]" in answer.upper():
        state.set(State.IDLE)
        return

    state.set(State.SPEAKING)
    tts.speak(answer)
    state.set(State.IDLE)


def run():
    if not prepare_model_path():
        return
    print("ASSISTANT STARTING")
    state = StateManager()
    try:
        if not init_models():
            print("[ERROR] Initialization failed.", flush=True)
            return
        while True:
            try:
                turn(state)
            except Exception:
                traceback.print_exc()
                tts.stop()
                state.set(State.IDLE)
    except KeyboardInterrupt:
        tts.stop()
        print("EXIT")


if __name__ == "__main__":
    run()
