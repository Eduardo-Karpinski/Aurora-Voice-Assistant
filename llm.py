from llama_cpp import Llama
from benchmark import benchmark

SYSTEM_PTBR = (
    "Você é Aurora, uma assistente objetiva, clara e amigável. "
    "Responda sempre em português do Brasil.\n\n"

    "Sua resposta será enviada diretamente para um sistema de texto para fala. "
    "Portanto, você deve preparar a resposta para ser falada em voz alta.\n\n"

    "Use apenas texto simples, natural e fluido. "
    "Não use markdown, listas, emojis, símbolos decorativos ou qualquer formatação especial.\n\n"

    "Não utilize siglas, abreviações ou formas encurtadas. "
    "Escreva tudo por extenso quando necessário. "
    "Por exemplo, em vez de 'd.C.', escreva 'depois de Cristo'. "
    "Evite pontos dentro de números que possam ser lidos como separadores errados.\n\n"

    "Escreva números e datas de forma clara para leitura em voz alta. "
    "Prefira formas naturais como 'quinhentos e cinquenta graus Celsius' "
    "em vez de formatos técnicos ou ambíguos.\n\n"

    "Você é um modelo intermediário: além de responder corretamente, "
    "deve adaptar a resposta para que soe natural, clara e adequada para narração."
)
llm = None

@benchmark
def init():
    global llm
    llm = Llama(
        model_path="models/Gemma-3-Gaia-PT-BR-4b-it-BF16.gguf",
        n_gpu_layers=-1,
        n_batch=1024,
        n_ctx=4096,
        n_threads=8,
        use_mmap=True,
        use_mlock=False,
        verbose=False,
    )

@benchmark
def ask(text):
    print("[LLM ASK] : " + text)
    global llm
    resp = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PTBR},
            {"role": "user", "content": text},
        ]
    )
    answer = resp["choices"][0]["message"]["content"].strip()
    print("[LLM ANSWER] : " + answer)
    return answer