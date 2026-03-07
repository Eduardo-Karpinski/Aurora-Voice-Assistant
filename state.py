from enum import Enum, auto

class State(Enum):
    IDLE = auto()          # aguardando wake word
    LISTENING = auto()     # capturando áudio
    TRANSCRIBING = auto()  # whisper
    THINKING = auto()      # LLM
    SPEAKING = auto()      # TTS
    
class StateManager:
    def __init__(self):
        self.state = State.IDLE

    def set(self, new_state):
        if self.state != new_state:
            print(f"[STATE] {self.state.name} -> {new_state.name}")
            self.state = new_state

    def is_state(self, state):
        return self.state == state