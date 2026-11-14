import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("COQUI_TOS_AGREED", "1")
# 3 = errors only. MIOpen warns while it rejects convolution solvers during XTTS tuning.
os.environ.setdefault("MIOPEN_LOG_LEVEL", "3")

import recorder
import transcription
import llm
import tts
import utils
from config import LLMConfig
from state import State, StateManager
import threading
from benchmark import benchmark

def prepare_model_path():
    path = LLMConfig.MODEL_PATH
    if not os.path.isabs(path):
        root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(root, path)
    LLMConfig.MODEL_PATH = path
    if os.path.isfile(path):
        return True
    print(f"[AVISO] Modelo não encontrado: {path}")
    print("[AVISO] Coloque o arquivo GGUF nessa pasta e inicie de novo.")
    return False

def _run_init(target, errors):
    try:
        target()
    except Exception as exc:
        errors.append(exc)
        print(f"[ERRO] {target.__name__}: {exc}", flush=True)

@benchmark
def init_models():
    errors = []
    print("[INIT] Carregando Whisper e XTTS. Na primeira vez o XTTS baixa o modelo.", flush=True)
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

if __name__ == "__main__":
    if prepare_model_path():
        try:
            print('ASSISTANT STARTING')
            state = StateManager()
            if not init_models():
                print("[ERRO] A inicialização falhou.", flush=True)
            else:
                while True:
                    state.set(State.LISTENING)
                    audio = recorder.record_until_silence(state)

                    state.set(State.TRANSCRIBING)
                    text = transcription.transcribe(audio)

                    valid, clean_text = utils.validate_transcript(text)

                    if not valid:
                        state.set(State.IDLE)
                        continue

                    tts.stop()

                    state.set(State.THINKING)
                    answer = llm.ask(clean_text)

                    if "[STOP]" in answer.upper():
                        tts.stop()
                        state.set(State.IDLE)
                        continue

                    state.set(State.SPEAKING)
                    threading.Thread(target=tts.speak, args=(answer,), daemon=True).start()
        except KeyboardInterrupt:
            print('EXIT')