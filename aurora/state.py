from enum import Enum, auto

class State(Enum):
    IDLE = auto()
    LISTENING = auto()
    RECORDING = auto()
    STOPPING_RECORDING = auto()
    TRANSCRIBING = auto()
    THINKING = auto()
    SPEAKING = auto()
    
class StateManager:
    def __init__(self):
        self.state = State.IDLE

    def set(self, new_state):
        if self.state != new_state:
            print(f"[STATE] {self.state.name} -> {new_state.name}")
            self.state = new_state

    def is_state(self, state):
        return self.state == state