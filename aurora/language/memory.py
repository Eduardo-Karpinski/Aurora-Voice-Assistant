def trim_messages(messages, count_tokens, budget):
    kept = [dict(message) for message in messages]
    while len(kept) > 1 and count_tokens(kept) > budget:
        kept.pop(0)
        if kept and kept[0]["role"] == "assistant":
            kept.pop(0)
    return kept


def estimate_tokens(messages, tokenize, overhead):
    total = 0
    for message in messages:
        content = message["content"].encode("utf-8")
        total += overhead + len(tokenize(content, add_bos=False))
    return total


class ConversationMemory:
    def __init__(self):
        self.messages = []

    def add_user(self, text):
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text):
        self.messages.append({"role": "assistant", "content": text})

    def drop_last(self):
        if self.messages:
            self.messages.pop()

    def trim(self, count_tokens, budget):
        self.messages = trim_messages(self.messages, count_tokens, budget)

    def turns(self):
        return sum(1 for message in self.messages if message["role"] == "user")
