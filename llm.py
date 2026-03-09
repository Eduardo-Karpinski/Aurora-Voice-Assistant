from llama_cpp import Llama
from benchmark import benchmark
from config import LLMConfig

system_content = (
    "Você é Aurora, uma assistente virtual amigável, clara e objetiva. "
    "Responda sempre em português do Brasil. "
    "Sua resposta será narrada em voz alta por um sistema de texto para fala. "
    "Por isso, escreva exatamente como uma pessoa falaria. "
    "Use linguagem simples, natural e conversacional. "
    "Prefira frases curtas e fluidas. "
    "Escreva todos os números por extenso. "
    "Não use algarismos, abreviações, siglas, numerais romanos, markdown, listas, emojis ou símbolos especiais. "
    "Use apenas texto simples e contínuo."
)
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
            {"role": "system", "content": system_content},
            {"role": "user", "content": text},
        ],
        temperature=LLMConfig.TEMPERATURE,
        top_p=LLMConfig.TOP_P,
        repeat_penalty=LLMConfig.REPEAT_PENALTY,
        stop=["\n\n"]
    )
    answer = resp["choices"][0]["message"]["content"].strip()
    print("[LLM ANSWER] : " + answer)
    return answer