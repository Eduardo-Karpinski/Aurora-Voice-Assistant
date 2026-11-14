from llama_cpp import Llama
from benchmark import benchmark
from config import LLMConfig
from memory import ConversationMemory, estimate_tokens

llm = None
memory = ConversationMemory()

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

@benchmark
def ask(text):
    print("[LLM ASK] : " + text)
    global llm
    memory.add_user(text)
    try:
        memory.trim(_history_tokens, _history_budget())
        tokens = _history_tokens(memory.messages)
        label = "turno" if memory.turns() == 1 else "turnos"
        print(f"[MEMORY] {memory.turns()} {label}, ~{tokens} tokens")
        resp = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": LLMConfig.SYSTEM_CONTENT},
                *memory.messages,
            ],
            temperature=LLMConfig.TEMPERATURE,
            top_p=LLMConfig.TOP_P,
            repeat_penalty=LLMConfig.REPEAT_PENALTY,
            max_tokens=LLMConfig.MAX_TOKENS,
        )
        answer = resp["choices"][0]["message"]["content"].strip()
    except Exception:
        memory.drop_last()
        raise
    print("[LLM ANSWER] : " + answer)
    if not answer or "[STOP]" in answer.upper():
        memory.drop_last()
        return answer
    memory.add_assistant(answer)
    return answer