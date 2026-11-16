import re
import unicodedata

from aurora.config import TTSConfig, WakeWordConfig

CHUNK_LIMIT = TTSConfig.CHUNK_LIMIT


def _produce_audio(parts, audio_queue, generate_audio):
    try:
        for part in parts:
            wav = generate_audio(part)
            audio_queue.put(wav)
    except Exception as exc:
        audio_queue.put(exc)
    finally:
        audio_queue.put(None)


def _chunk_text(text: str):
    text = text.strip()
    parts = []
    while len(text) > CHUNK_LIMIT:
        comma = text.rfind(", ", 0, CHUNK_LIMIT)
        space = text.rfind(" ", 0, CHUNK_LIMIT)
        if comma > 0:
            part = text[:comma + 1].strip()
            text = text[comma + 2:].strip()
        elif space > 0:
            part = text[:space].strip()
            text = text[space + 1:].strip()
        else:
            part = text[:CHUNK_LIMIT].strip()
            text = text[CHUNK_LIMIT:].strip()
        if not part:
            break
        parts.append(part)
    if text:
        parts.append(text)
    return parts


def _select_device():
    import torch

    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        print(f"[DEVICE] USING {name}")
        return torch.device("cuda")

    print("[DEVICE] USING CPU")
    return torch.device("cpu")


def _prepare_for_tts(text):
    text = text.strip()

    while re.search(r"(\d)\.(\d{3})\b", text):
        text = re.sub(r"(\d)\.(\d{3})\b", r"\1\2", text)

    text = re.sub(r"(?<!\.)\.(?!\.)", ",", text)

    text = re.sub(r"\s+([,!?;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


_XTTS_LANGUAGES = {
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar",
    "zh-cn", "hu", "ko", "ja", "hi",
}

_SCRIPT_LANGUAGES = (
    (re.compile(r"[\u3040-\u30ff]"), "ja"),
    (re.compile(r"[\uac00-\ud7af]"), "ko"),
    (re.compile(r"[\u0600-\u06ff]"), "ar"),
    (re.compile(r"[\u0400-\u04ff]"), "ru"),
    (re.compile(r"[\u0900-\u097f]"), "hi"),
    (re.compile(r"[\u4e00-\u9fff]"), "zh-cn"),
)

_LANGUAGE_WORDS = {
    "pt": {"não", "nao", "você", "voce", "vocês", "voces", "obrigado", "obrigada", "também", "tambem", "olá", "ola", "está", "estão", "estao", "isso", "aqui", "muito", "porque", "sim", "pra"},
    "es": {"hola", "gracias", "usted", "qué", "cómo", "buenos", "buenas", "español", "espanol", "hoy", "también"},
    "en": {"the", "what", "how", "this", "that", "with", "hello", "thanks", "thank", "you", "are", "was", "have", "from", "about", "weather", "degrees", "minus", "please", "yes"},
    "fr": {"bonjour", "merci", "vous", "avec", "aujourd", "oui", "français", "francais", "une", "pour"},
    "de": {"danke", "bitte", "nicht", "und", "wie", "das", "ist", "wetter", "heute", "hallo", "für", "fur"},
    "it": {"ciao", "grazie", "buongiorno", "perché", "perche", "sono", "oggi"},
    "pl": {"dzięki", "dzieki", "dziękuję", "dziekuje", "się", "sie", "proszę", "prosze", "dzień", "dzien"},
    "nl": {"dank", "niet", "vandaag", "hallo", "alstublieft", "hoe"},
    "tr": {"merhaba", "teşekkürler", "tesekkurler", "değil", "degil", "nasıl", "nasil", "bugün", "bugun"},
    "cs": {"děkuji", "dekuji", "ahoj", "prosím", "prosim", "dnes", "není", "neni"},
    "hu": {"köszönöm", "koszonom", "szia", "hogy", "vagyok"},
}

_LANGUAGE_MARKS = (
    ("pt", re.compile(r"[ãõ]")),
    ("es", re.compile(r"[ñ¿¡]")),
    ("de", re.compile(r"[ß]")),
    ("pl", re.compile(r"[ąęł]")),
    ("cs", re.compile(r"[ěřů]")),
    ("hu", re.compile(r"[őű]")),
    ("tr", re.compile(r"[ğşı]")),
)


def speech_language(text, default=None):
    if default is None:
        default = TTSConfig.LANGUAGE if TTSConfig.LANGUAGE in _XTTS_LANGUAGES else "pt"
    if not text or not str(text).strip():
        return default
    for pattern, code in _SCRIPT_LANGUAGES:
        if pattern.search(text):
            return code
    tokens = set(re.findall(r"[^\W\d_]+", text.lower()))
    scores = {
        code: sum(1 for token in tokens if token in words)
        for code, words in _LANGUAGE_WORDS.items()
    }
    for code, pattern in _LANGUAGE_MARKS:
        if pattern.search(text.lower()):
            scores[code] += 2
    best = max(scores, key=lambda code: (scores[code], code == default))
    if scores[best] == 0:
        return default
    return best


def _fold(text):
    folded = []
    indexes = []
    for index, char in enumerate(text):
        for piece in unicodedata.normalize("NFD", char):
            if unicodedata.category(piece) == "Mn":
                continue
            folded.append(piece.lower())
            indexes.append(index)
    return "".join(folded), indexes


def validate_transcript(text: str, wake_word: str = None):
    if wake_word is None:
        wake_word = WakeWordConfig.WORD
    if not text or not str(text).strip():
        print("[VALIDATION] Empty text, ignoring.")
        return False, None
    original = str(text).strip()
    if not wake_word:
        return True, original
    folded, indexes = _fold(original)
    word, _ = _fold(wake_word.strip())
    match = re.search(rf"^{re.escape(word)}\b[,:;\-–—.!?]*\s*(.*)$", folded)
    if not match:
        print(f"[VALIDATION] Wake word missing, ignoring: {original}")
        return False, None
    start = match.start(1)
    command = original[indexes[start]:].strip() if start < len(indexes) else ""
    if not re.search(r"[\w]", command):
        print("[VALIDATION] Wake word only, ignoring.")
        return False, None
    return True, command
