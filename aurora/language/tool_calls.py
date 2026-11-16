import json
import re

_TOOL_BLOCK = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_THINK_BLOCK = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)
_FUNCTION_BLOCK = re.compile(r"<function=([^>\n]+)>(.*?)</function>", re.DOTALL)
_PARAMETER = re.compile(r"<parameter=([^>\n]+)>\s*(.*?)\s*</parameter>", re.DOTALL)


def parse_tool_call(text):
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


def call_from(content, tool_calls):
    parsed = parse_tool_call(content)
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


def spoken_answer(text):
    text = _TOOL_BLOCK.sub("", text or "")
    text = _THINK_BLOCK.sub("", text)
    return " ".join(text.split())
