import re
import unicodedata

WAKE_WORD = "aurora"

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
        return False

    normalized = _normalize(text)
    pattern = rf"^\s*\b{re.escape(wake_word)}\b[,:;\-–—]?\s*(.*)$"
    match = re.search(pattern, normalized)

    if not match:
        print(f"[WAKEWORD] REJECTED — '{text}'")
        return False

    return True