import recorder
import transcription
import llm
import tts
import wakeword
from state import State, StateManager
import threading

def main():
    state = StateManager()
    
    t1 = threading.Thread(target=transcription.init, name="Transcription-Thread")
    t2 = threading.Thread(target=tts.init, name="TTS-Thread")
    t3 = threading.Thread(target=llm.init, name="LLM-Thread")

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    
    while True:
        state.set(State.LISTENING)
        audio = recorder.record_until_silence(state)
        
        state.set(State.TRANSCRIBING)
        text = transcription.transcribe(audio)
        
        valid, clean_text = wakeword.validate(text)
        
        if not valid:
            state.set(State.IDLE)
            continue
        
        state.set(State.THINKING)
        answer = llm.ask(clean_text)
        
        state.set(State.SPEAKING)
        tts.speak(answer)
        
        state.set(State.IDLE)

if __name__ == "__main__":
    try:
        print('ASSISTANT STARTING')
        main()
    except KeyboardInterrupt:
        print('EXIT')