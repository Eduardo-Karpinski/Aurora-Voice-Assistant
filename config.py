class LLMConfig:
    MODEL_PATH = "models/Gemma-3-Gaia-PT-BR-4b-it-BF16.gguf"
    N_GPU_LAYERS = -1
    N_BATCH = 1024
    N_CTX = 4096
    N_THREADS = 8
    USE_MMAP = True
    USE_MLOCK = False
    VERBOSE = False
    TEMPERATURE = 0.0
    TOP_P = 0.9
    REPEAT_PENALTY = 1.1

class TranscriptionConfig:
    MODEL_SIZE = "medium"
    DEVICE = "cpu"
    COMPUTE_TYPE = "int8"
    LANGUAGE = "pt"
    BEAM_SIZE = 1
    VAD_FILTER = False
    TEMPERATURE = 0.1
    CONDITION_ON_PREVIOUS_TEXT = False

class RecorderConfig:
    SAMPLE_RATE = 16000
    FRAME_MS = 30
    VAD_MODE = 3
    START_VOICE_FRAMES = 5
    SILENCE_FRAMES_TO_STOP = 25
    PRE_ROLL_FRAMES = 10

class TTSConfig:
    MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
    SPEAKER = "Alma María"
    LANGUAGE = "pt"
    SAMPLE_RATE = 24000
    CHUNK_LIMIT = 180

class WakeWordConfig:
    WORD = "aurora"