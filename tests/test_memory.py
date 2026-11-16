from aurora.language.memory import ConversationMemory, estimate_tokens, trim_messages


def _count_by_length(messages):
    return len(messages)


def test_trim_drops_the_oldest_user_turn_and_its_reply():
    messages = [
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "c"},
        {"role": "assistant", "content": "d"},
    ]
    kept = trim_messages(messages, _count_by_length, budget=2)
    assert kept == [
        {"role": "user", "content": "c"},
        {"role": "assistant", "content": "d"},
    ]
    assert messages[0]["content"] == "a"


def test_trim_keeps_the_last_message_even_when_it_is_over_budget():
    messages = [{"role": "user", "content": "only"}]
    assert trim_messages(messages, lambda kept: 999, budget=1) == messages


def test_estimate_tokens_adds_overhead_for_each_message():
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "á"},
    ]

    def tokenize(text, add_bos=False):
        assert add_bos is False
        return text

    expected = 12 + len("hi".encode()) + 12 + len("á".encode())
    assert estimate_tokens(messages, tokenize, overhead=12) == expected


def test_memory_tracks_turns_and_drops_the_latest_message():
    memory = ConversationMemory()
    memory.add_user("São Paulo")
    memory.add_assistant("noted")
    assert memory.turns() == 1
    memory.drop_last()
    assert memory.messages == [{"role": "user", "content": "São Paulo"}]
    memory.drop_last()
    memory.drop_last()
    assert memory.messages == []


def test_memory_trim_uses_the_supplied_budget():
    memory = ConversationMemory()
    memory.add_user("a")
    memory.add_assistant("b")
    memory.add_user("c")
    memory.trim(_count_by_length, budget=1)
    assert memory.messages == [{"role": "user", "content": "c"}]
