import os

class LLMConfig:
    MODEL_PATH = "models/Qwen3-8B-Q5_K_M.gguf"
    N_GPU_LAYERS = -1
    N_BATCH = 1024
    N_CTX = 4096
    N_THREADS = 8
    USE_MMAP = True
    USE_MLOCK = False
    VERBOSE = False
    TEMPERATURE = 0.7
    TOP_P = 0.8
    TOP_K = 20
    MIN_P = 0.0
    REPEAT_PENALTY = 1.1
    PRESENCE_PENALTY = 1.0
    MAX_TOKENS = 256
    CONTEXT_MARGIN = 64
    MESSAGE_OVERHEAD = 12
    SYSTEM_CONTENT = (
        "You are Aurora, a friendly, clear, and direct virtual assistant. "
        "Always reply in the same language the user used to ask. "
        "Your reply will be read aloud by a text-to-speech system. "
        "Write exactly the way a person would speak. "
        "Use simple, natural, conversational language. "
        "Prefer short, flowing sentences. "
        "Write every number in words, in the language of the reply. "
        "Temperatures below zero and any negative quantity start with the word for minus in that language, as in menos cinco graus or minus five degrees. "
        "Do not use digits, abbreviations, acronyms, Roman numerals, markdown, lists, emoji, or special symbols. "
        "Use only plain, continuous text. "
        "When the question depends on a current fact, news, weather, a price, or anything you are not sure about, call the search tool before answering. "
        "The spoken reply is still plain text only. "
        "IMPORTANT: If the user asks you to stop, be quiet, or says stop, parar, cala a boca, chega, or any other interruption, reply with the single word [STOP] and nothing else."
    )

class TranscriptionConfig:
    MODEL_SIZE = "medium"
    DEVICE = "cuda"
    COMPUTE_TYPE = "float16"
    # None detects the spoken language on each turn.
    LANGUAGE = None
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
    DTYPE = "float32"

class TTSConfig:
    MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
    SPEAKER = "Alma María"
    # Used when the reply language cannot be told apart. XTTS also receives the detected language.
    LANGUAGE = "pt"
    SAMPLE_RATE = 24000
    CHUNK_LIMIT = 180

class SearchConfig:
    REGION = "br-pt"
    MAX_RESULTS = 5
    SNIPPET_LIMIT = 240
    PAGE_LIMIT = 800
    TIMEOUT = 12

class WakeWordConfig:
    # The phrase must start with this word. An empty string listens to every phrase.
    WORD = "aurora"

class DebugConfig:
    BENCHMARK = os.environ.get("AURORA_BENCHMARK", "").strip().lower() in {"1", "true", "yes", "on"}
