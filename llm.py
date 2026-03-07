from llama_cpp import Llama
from benchmark import benchmark
from config import LLMConfig

SYSTEM_PTBR = (
    "Você é Aurora, uma assistente objetiva, clara e amigável. "
    "Responda sempre em português do Brasil.\n\n"

    "Sua resposta será enviada diretamente para um sistema de texto para fala. "
    "Portanto, escreva a resposta como se estivesse sendo narrada em voz alta.\n\n"

    "REGRAS OBRIGATÓRIAS:\n"
    "Não use abreviações, siglas ou numerais romanos.\n"
    "Não escreva expressões como a C, d C, século XV, século XIX ou similares.\n"
    "Escreva tudo por extenso.\n\n"

    "Exemplos corretos:\n"
    "trezentos anos antes de Cristo\n"
    "século quinze\n"
    "século dezenove\n\n"

    "Use apenas texto simples, natural e fluido. "
    "Não use markdown, listas, emojis ou símbolos especiais."
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
            {"role": "system", "content": SYSTEM_PTBR},
            {"role": "user", "content": text},
        ],
        temperature=LLMConfig.TEMPERATURE,
        top_p=LLMConfig.TOP_P,
        repeat_penalty=LLMConfig.REPEAT_PENALTY,
    )
    answer = resp["choices"][0]["message"]["content"].strip()
    print("[LLM ANSWER] : " + answer)
    return answer