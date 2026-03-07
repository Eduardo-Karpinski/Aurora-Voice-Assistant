import recorder
import transcription
import llm
import tts
import wakeword
from state import State, StateManager

def main():
    state = StateManager()
    transcription.init()
    tts.init()
    llm.init()
    
    while True:
        state.set(State.LISTENING)
        audio = recorder.record_until_silence()
        
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
        print('START SYSTEM')
        main()
    except KeyboardInterrupt:
        print('BYE')