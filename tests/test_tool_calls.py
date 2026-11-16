from tool_calls import call_from, parse_tool_call, spoken_answer


def test_parse_tool_call_reads_a_json_payload():
    text = """
    Looking it up.
    <tool_call>
    {"name": "search", "arguments": "{\\"query\\": \\"dollar rate\\"}"}
    </tool_call>
    """
    assert parse_tool_call(text) == ("search", {"query": "dollar rate"})


def test_parse_tool_call_reads_a_function_block():
    text = """
    <tool_call>
    <function=search>
    <parameter=query>
    dollar rate
    </parameter>
    </function>
    </tool_call>
    """
    assert parse_tool_call(text) == ("search", {"query": "dollar rate"})


def test_parse_tool_call_rejects_broken_json():
    assert parse_tool_call('<tool_call>{"name":</tool_call>') is None
    assert parse_tool_call("no tool here") is None
    assert parse_tool_call("") is None


def test_call_from_prefers_the_message_text():
    tool_calls = [{"function": {"name": "search", "arguments": {"query": "ignored"}}}]
    content = '<tool_call>{"name": "search", "arguments": {"query": "from text"}}</tool_call>'
    assert call_from(content, tool_calls) == ("search", {"query": "from text"})


def test_call_from_uses_the_structured_tool_call():
    tool_calls = [{"function": {"name": "search", "arguments": "{\"query\": \"weather\"}"}}]
    assert call_from("I will check.", tool_calls) == ("search", {"query": "weather"})
    assert call_from("nothing", []) is None
    assert call_from("nothing", [{"function": {}}]) is None


def test_spoken_answer_removes_tool_and_thinking_markup():
    text = "<think>draft</think> The rate is five. <tool_call>{}</tool_call>"
    assert spoken_answer(text) == "The rate is five."
    assert spoken_answer("<think>still thinking") == ""
    assert spoken_answer(None) == ""
