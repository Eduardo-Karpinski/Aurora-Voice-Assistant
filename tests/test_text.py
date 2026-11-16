import queue

from config import TTSConfig
from utils import _chunk_text, _prepare_for_tts, _produce_audio, speech_language, validate_transcript


def test_speech_language_follows_the_reply():
    assert speech_language("A temperatura está em menos cinco graus.") == "pt"
    assert speech_language("The temperature is minus five degrees.") == "en"
    assert speech_language("Hola, gracias por preguntar hoy.") == "es"
    assert speech_language("今日の天気は晴れです。") == "ja"
    assert speech_language("ok") == "pt"


def test_validate_transcript_keeps_the_command_case_and_accents():
    valid, text = validate_transcript("  Aurora, São Paulo está quente.  ")
    assert valid is True
    assert text == "São Paulo está quente."
    assert validate_transcript("AURORA what time is it")[1] == "what time is it"
    assert validate_transcript("Áurora: oi")[1] == "oi"


def test_validate_transcript_ignores_speech_without_the_wake_word():
    assert validate_transcript("São Paulo está quente.") == (False, None)
    assert validate_transcript("The aurora is bright") == (False, None)
    assert validate_transcript("Aurora") == (False, None)
    assert validate_transcript("São Paulo", wake_word="")[1] == "São Paulo"


def test_validate_transcript_rejects_blank_text():
    assert validate_transcript("   ") == (False, None)
    assert validate_transcript("") == (False, None)
    assert validate_transcript(None) == (False, None)


def test_prepare_for_tts_collapses_thousands_and_sentence_periods():
    prepared = _prepare_for_tts("  Total is 1.000.000. Wait...  done . ")
    assert prepared == "Total is 1000000, Wait... done,"


def test_chunk_text_keeps_the_comma_and_finishes():
    head = "a" * 100
    text = f"{head}, " + ("b" * 200)
    assert _chunk_text(text) == [
        head + ",",
        "b" * TTSConfig.CHUNK_LIMIT,
        "b" * (200 - TTSConfig.CHUNK_LIMIT),
    ]


def test_chunk_text_keeps_a_short_line_intact():
    assert _chunk_text("  a short sentence  ") == ["a short sentence"]


def test_produce_audio_forwards_generation_errors():
    audio = queue.Queue()

    def generate(part):
        raise RuntimeError(part)

    _produce_audio(["hello"], audio, generate)
    error = audio.get_nowait()
    assert isinstance(error, RuntimeError)
    assert str(error) == "hello"
    assert audio.get_nowait() is None
