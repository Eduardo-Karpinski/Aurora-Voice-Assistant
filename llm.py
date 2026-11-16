from llama_cpp import Llama

from benchmark import benchmark
from config import LLMConfig
from memory import ConversationMemory, estimate_tokens
from search import search
from tool_calls import call_from, spoken_answer

llm = None
memory = ConversationMemory()

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search",
        "description": (
            "Search the web for current facts, news, weather, prices, "
            "or anything that must not be invented."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Short search query.",
                }
            },
            "required": ["query"],
        },
    },
}


@benchmark
def init():
    global llm
    llm = Llama(
        model_path=LLMConfig.MODEL_PATH,
        n_gpu_layers=LLMConfig.N_GPU_LAYERS,
        n_batch=LLMConfig.N_BATCH,
        n_ctx=LLMConfig.N_CTX,
        n_threads=LLMConfig.N_THREADS,
        use_mmap=LLMConfig.USE_MMAP,
        use_mlock=LLMConfig.USE_MLOCK,
        verbose=LLMConfig.VERBOSE,
    )
    _speak_without_thinking()


def _speak_without_thinking():
    handler = llm._chat_handlers.get(llm.chat_format)
    if handler is None:
        return

    def chat_handler(**kwargs):
        kwargs["enable_thinking"] = False
        return handler(**kwargs)

    llm.chat_handler = chat_handler


def _complete(messages, tools=None):
    options = {
        "messages": messages,
        "temperature": LLMConfig.TEMPERATURE,
        "top_p": LLMConfig.TOP_P,
        "top_k": LLMConfig.TOP_K,
        "min_p": LLMConfig.MIN_P,
        "repeat_penalty": LLMConfig.REPEAT_PENALTY,
        "presence_penalty": LLMConfig.PRESENCE_PENALTY,
        "max_tokens": LLMConfig.MAX_TOKENS,
    }
    if tools:
        options["tools"] = tools
    response = llm.create_chat_completion(**options)
    message = response["choices"][0]["message"]
    return message.get("content") or "", message.get("tool_calls") or []


def _tokenize(text, add_bos=False):
    return llm.tokenize(text, add_bos=add_bos)


def _history_tokens(messages):
    return estimate_tokens(messages, _tokenize, LLMConfig.MESSAGE_OVERHEAD)


def _history_budget():
    system_tokens = estimate_tokens(
        [{"role": "system", "content": LLMConfig.SYSTEM_CONTENT}],
        _tokenize,
        LLMConfig.MESSAGE_OVERHEAD,
    )
    return LLMConfig.N_CTX - LLMConfig.MAX_TOKENS - LLMConfig.CONTEXT_MARGIN - system_tokens


def _query_from(arguments):
    return arguments.get("query") or arguments.get("consulta") or ""


@benchmark
def ask(text):
    print("[LLM ASK] : " + text)
    global llm
    memory.add_user(text)
    try:
        memory.trim(_history_tokens, _history_budget())
        tokens = _history_tokens(memory.messages)
        label = "turn" if memory.turns() == 1 else "turns"
        print(f"[MEMORY] {memory.turns()} {label}, ~{tokens} tokens")
        messages = [
            {"role": "system", "content": LLMConfig.SYSTEM_CONTENT},
            *memory.messages,
        ]
        content, tool_calls = _complete(messages, tools=[SEARCH_TOOL])
        if "[STOP]" not in content.upper():
            call = call_from(content, tool_calls)
            # Older replies used the names "pesquisar" and "consulta".
            if call and call[0] in {"search", "pesquisar"}:
                query = _query_from(call[1])
                print(f"[SEARCH] {query}", flush=True)
                result = search(query)
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": f"<tool_response>\n{result}\n</tool_response>",
                })
                content, _ = _complete(messages)
        answer = spoken_answer(content)
    except Exception:
        memory.drop_last()
        raise
    print("[LLM ANSWER] : " + answer)
    if not answer or "[STOP]" in answer.upper():
        memory.drop_last()
        return answer
    memory.add_assistant(answer)
    return answer
