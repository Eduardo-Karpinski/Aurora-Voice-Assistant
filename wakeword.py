import re
import unicodedata
from config import WakeWordConfig

WAKE_WORD = WakeWordConfig.WORD

def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )
    text = re.sub(r"\s+", " ", text)
    return text

def validate(text: str, wake_word: str = WAKE_WORD):
    if not text or not text.strip():
        print("[WAKEWORD] EMPTY TEXT — IGNORING")
        return False, None

    normalized = _normalize(text)
    pattern = rf"^\s*\b{re.escape(wake_word)}\b[,:;\-–—]?\s*(.*)$"
    match = re.search(pattern, normalized)

    if not match:
        print(f"[WAKEWORD] REJECTED — '{text}'")
        return False, None

    command = match.group(1).strip()
    print(f"[WAKEWORD] ACCEPTED — '{command}'")
    return True, command