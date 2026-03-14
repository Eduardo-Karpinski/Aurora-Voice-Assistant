import recorder
import transcription
import llm
import tts
import utils
from state import State, StateManager
import threading
from benchmark import benchmark

@benchmark
def init_models():
    t1 = threading.Thread(target=transcription.init, name="Transcription-Thread")
    t2 = threading.Thread(target=tts.init, name="TTS-Thread")
    t3 = threading.Thread(target=llm.init, name="LLM-Thread")

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

if __name__ == "__main__":
    try:
        print('ASSISTANT STARTING')
        state = StateManager()
        init_models()
        
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