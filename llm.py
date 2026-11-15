import json
import re
from llama_cpp import Llama
from benchmark import benchmark
from config import LLMConfig
from memory import ConversationMemory, estimate_tokens
from search import pesquisar

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
    _speak_without_thinking()

def _speak_without_thinking():
    handler = llm._chat_handlers.get(llm.chat_format)
    if handler is None:
        return

    def chat_handler(**kwargs):
        kwargs["enable_thinking"] = False
        return handler(**kwargs)

    llm.chat_handler = chat_handler

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "pesquisar",
        "description": (
            "Pesquisa na internet por fatos atuais, notícias, clima, preços "
            "ou qualquer informação que não deva ser inventada."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "consulta": {
                    "type": "string",
                    "description": "Texto objetivo da pesquisa.",
                }
            },
            "required": ["consulta"],
        },
    },
}

_TOOL_BLOCK = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_FUNCTION_BLOCK = re.compile(r"<function=([^>\n]+)>(.*?)</function>", re.DOTALL)
_PARAMETER = re.compile(r"<parameter=([^>\n]+)>\s*(.*?)\s*</parameter>", re.DOTALL)

def _parse_tool_call(text):
    if not text:
        return None
    match = _TOOL_BLOCK.search(text)
    if not match:
        return None
    body = match.group(1).strip()
    if body.startswith("{"):
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return None
        name = data.get("name")
        arguments = data.get("arguments") or {}
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}
        if not name:
            return None
        return name, arguments if isinstance(arguments, dict) else {}
    function = _FUNCTION_BLOCK.search(body)
    if not function:
        return None
    arguments = {
        item.group(1).strip(): item.group(2).strip()
        for item in _PARAMETER.finditer(function.group(2))
    }
    return function.group(1).strip(), arguments

def _call_from(content, tool_calls):
    parsed = _parse_tool_call(content)
    if parsed:
        return parsed
    if not tool_calls:
        return None
    function = tool_calls[0].get("function") or {}
    name = function.get("name")
    arguments = function.get("arguments") or {}
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {}
    if not name:
        return None
    return name, arguments if isinstance(arguments, dict) else {}

def _spoken_answer(text):
    text = _TOOL_BLOCK.sub("", text or "")
    text = text.replace("<think>", "").replace("</think>", "")
    return text.strip()

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
        messages = [
            {"role": "system", "content": LLMConfig.SYSTEM_CONTENT},
            *memory.messages,
        ]
        content, tool_calls = _complete(messages, tools=[SEARCH_TOOL])
        if "[STOP]" not in content.upper():
            call = _call_from(content, tool_calls)
            if call and call[0] == "pesquisar":
                consulta = call[1].get("consulta") or call[1].get("query") or ""
                print(f"[SEARCH] {consulta}", flush=True)
                result = pesquisar(consulta)
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": f"<tool_response>\n{result}\n</tool_response>",
                })
                content, _ = _complete(messages)
        answer = _spoken_answer(content)
    except Exception:
        memory.drop_last()
        raise
    print("[LLM ANSWER] : " + answer)
    if not answer or "[STOP]" in answer.upper():
        memory.drop_last()
        return answer
    memory.add_assistant(answer)
    return answer