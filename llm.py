from llama_cpp import Llama
from benchmark import benchmark
from config import LLMConfig

llm = None

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

@benchmark
def ask(text):
    print("[LLM ASK] : " + text)
    global llm
    resp = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": LLMConfig.SYSTEM_CONTENT},
            {"role": "user", "content": text},
        ],
        temperature=LLMConfig.TEMPERATURE,
        top_p=LLMConfig.TOP_P,
        repeat_penalty=LLMConfig.REPEAT_PENALTY
    )
    answer = resp["choices"][0]["message"]["content"].strip()
    print("[LLM ANSWER] : " + answer)
    return answer