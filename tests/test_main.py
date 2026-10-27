import asyncio
import runpy
import sys
from importlib import import_module

import pytest
from mcp.client.stdio import StdioServerParameters
from mcp.shared.exceptions import MCPError

from ai_engineer_roadmap.memory import MemoryItem

main_module = import_module("ai_engineer_roadmap.main")
from ai_engineer_roadmap.conversation import ConversationState
from ai_engineer_roadmap.main import trim_messages_by_budget


def test_trim_messages_by_budget_keeps_latest_turn_if_it_exceeds_budget():
    messages = [
        {"role": "user", "content": "旧问题"},
        {"role": "assistant", "content": "旧回答"},
        {"role": "user", "content": "这是一个很长的新问题"},
        {"role": "assistant", "content": "这是一个很长的新回答"},
    ]

    result = trim_messages_by_budget(messages, max_chars=5)

    assert result == messages[2:]


def test_trim_messages_by_budget_keeps_latest_complete_turns():
    messages = [
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "A2"},
        {"role": "user", "content": "Q3"},
        {"role": "assistant", "content": "A3"},
    ]

    result = trim_messages_by_budget(messages, max_chars=8)

    assert result == messages[2:]
    assert len(messages) == 6


def test_build_context_messages_summarizes_omitted_prefix(monkeypatch):
    messages = [
        {"role": "user", "content": "旧问题"},
        {"role": "assistant", "content": "旧答案"},
        {"role": "user", "content": "新问题"},
        {"role": "assistant", "content": "新答案"},
    ]
    calls = []

    def fake_summarize(messages_to_summarize, existing_summary):
        calls.append((messages_to_summarize, existing_summary))
        return "早期对话摘要"

    monkeypatch.setattr(
        main_module, "summarize_messages", fake_summarize, raising=False
    )
    conversation = ConversationState(conversation_id=1, messages=messages)

    result = main_module.build_context_messages(conversation, max_chars=5)

    assert calls == [(messages[:2], "")]
    assert result[0]["role"] == "assistant"
    assert "早期对话摘要" in result[0]["content"]
    assert result[1:] == messages[2:]
    assert conversation.messages == messages
    assert conversation.summary == "早期对话摘要"
    assert conversation.summarized_message_count == 2


def test_build_memory_context_raises_for_negative_budget():
    with pytest.raises(ValueError, match="max_chars 不能小于 0"):
        main_module.build_memory_context([], max_chars=-1)


def test_build_memory_context_empty():
    assert main_module.build_memory_context([], max_chars=5) == ""


def test_build_memory_context_trims_to_budget():
    memory_items = [
        MemoryItem(content="记忆1", memory_id=1),
        MemoryItem(content="记忆2", memory_id=2),
        MemoryItem(content="记忆3", memory_id=3),
    ]

    result = main_module.build_memory_context(memory_items, max_chars=5)

    assert "记忆3" in result
    assert "记忆2" not in result
    assert "记忆1" not in result
    assert result == "- 记忆3"


def test_build_memory_context_returns_empty_when_budget_is_zero():
    items = [MemoryItem(content="记忆", memory_id=1)]
    assert main_module.build_memory_context(items, max_chars=0) == ""


def test_build_memory_context_skips_oversized_item_and_keeps_shorter_one():
    items = [
        MemoryItem(content="短", memory_id=1),
        MemoryItem(content="这条记忆很长", memory_id=2),
    ]
    result = main_module.build_memory_context(items, max_chars=len("- 短"))
    assert result == "- 短"


def test_build_memory_context_preserves_order_when_items_fit():
    items = [
        MemoryItem(content="甲", memory_id=1),
        MemoryItem(content="乙", memory_id=2),
    ]
    expected = "- 甲\n- 乙"
    assert main_module.build_memory_context(items, max_chars=len(expected)) == expected


def test_ask_agent_with_mcp_reports_mcp_error(monkeypatch):

    class FakeClient:
        def __init__(self, params):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    async def failing_ask(messages, mcp_client, memory_context):
        raise MCPError(-32000, "tool discovery failed")

    monkeypatch.setattr(main_module, "Client", FakeClient)
    monkeypatch.setattr(main_module, "ask_llm_with_tools", failing_ask)

    result = asyncio.run(
        main_module.ask_agent_with_mcp([{"role": "user", "content": "查看任务"}], "")
    )

    assert result == "MCP 工具暂时不可用，请稍后重试。"


@pytest.mark.parametrize(
    "error_type",
    [TypeError, ValueError, OSError, FileNotFoundError],
)
def test_ask_agent_with_mcp_propagates_unhandled_errors(monkeypatch, error_type):
    class FakeClient:
        def __init__(self, params):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    async def failing_ask(messages, mcp_client, memory_context):
        raise error_type("unexpected bug")

    monkeypatch.setattr(main_module, "Client", FakeClient)
    monkeypatch.setattr(main_module, "ask_llm_with_tools", failing_ask)

    with pytest.raises(error_type, match="unexpected bug"):
        asyncio.run(
            main_module.ask_agent_with_mcp(
                [{"role": "user", "content": "查看任务"}],
                "",
            )
        )


def test_ask_agent_with_mcp_preserves_normal_result(monkeypatch):
    received = {}
    lifecycle = []

    class FakeClient:
        def __init__(self, params):
            pass

        async def __aenter__(self):
            lifecycle.append("entered")
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            lifecycle.append("exited")
            return False

    async def successful_ask(messages, mcp_client, memory_context):
        received["messages"] = messages
        received["memory_context"] = memory_context
        assert isinstance(mcp_client, FakeClient)
        return "这是正常回答。"

    monkeypatch.setattr(main_module, "Client", FakeClient)
    monkeypatch.setattr(main_module, "ask_llm_with_tools", successful_ask)

    messages = [{"role": "user", "content": "查看任务"}]
    memory_context = "用户偏好简洁回答。"

    result = asyncio.run(main_module.ask_agent_with_mcp(messages, memory_context))

    assert result == "这是正常回答。"
    assert received["messages"] is messages
    assert received["memory_context"] == memory_context
    assert lifecycle == ["entered", "exited"]


def test_ask_agent_with_mcp_reports_server_start_failure(monkeypatch):
    class FailingClient:
        def __init__(self, params):
            pass

        async def __aenter__(self):
            raise FileNotFoundError("uv executable not found")

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    async def unexpected_ask(messages, mcp_client, memory_context):
        raise AssertionError("连接失败后不应调用 Agent")

    monkeypatch.setattr(main_module, "Client", FailingClient)
    monkeypatch.setattr(main_module, "ask_llm_with_tools", unexpected_ask)

    result = asyncio.run(
        main_module.ask_agent_with_mcp(
            [{"role": "user", "content": "查看任务"}],
            "",
        )
    )

    assert result == "MCP 服务启动失败，请检查本地启动配置。"


def test_ask_agent_with_real_mcp_client_reports_error(monkeypatch, tmp_path):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ai_engineer_roadmap.mcp_server"],
        cwd=tmp_path,
    )

    async def failing_ask(messages, mcp_client, memory_context):
        raise MCPError(-32000, "tool discovery failed")

    monkeypatch.setattr(main_module, "server_params", params)
    monkeypatch.setattr(main_module, "ask_llm_with_tools", failing_ask)

    result = asyncio.run(
        asyncio.wait_for(
            main_module.ask_agent_with_mcp(
                [{"role": "user", "content": "查看任务"}],
                "",
            ),
            timeout=20,
        )
    )

    assert result == "MCP 工具暂时不可用，请稍后重试。"


def test_ask_agent_with_real_client_preserves_mixed_errors(monkeypatch, tmp_path):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ai_engineer_roadmap.mcp_server"],
        cwd=tmp_path,
    )

    async def failing_ask(messages, mcp_client, memory_context):
        raise ExceptionGroup(
            "mixed failure",
            [
                MCPError(-32000, "tool discovery failed"),
                TypeError("unexpected bug"),
            ],
        )

    monkeypatch.setattr(main_module, "server_params", params)
    monkeypatch.setattr(main_module, "ask_llm_with_tools", failing_ask)

    with pytest.raises(ExceptionGroup) as caught:
        asyncio.run(
            asyncio.wait_for(
                main_module.ask_agent_with_mcp(
                    [{"role": "user", "content": "查看任务"}],
                    "",
                ),
                timeout=20,
            )
        )

    assert caught.value.subgroup(TypeError) is not None
    assert caught.value.subgroup(MCPError) is not None


def test_cli_continues_after_mcp_failure(monkeypatch, tmp_path, capsys):
    class FakeClient:
        def __init__(self, params):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    received_inputs = []

    async def fake_ask(messages, mcp_client, memory_context):
        received_inputs.append(messages[-1]["content"])

        if len(received_inputs) == 1:
            raise MCPError(-32000, "tool discovery failed")

        return "这是重试后的正常回答。"

    user_inputs = iter(["new", "查看任务", "再试一次", "exit"])

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(user_inputs))
    monkeypatch.setattr("mcp.Client", FakeClient)
    monkeypatch.setattr(
        "ai_engineer_roadmap.llm.ask_llm_with_tools",
        fake_ask,
    )

    with pytest.raises(SystemExit) as caught:
        runpy.run_path(main_module.__file__, run_name="__main__")

    output = capsys.readouterr().out

    assert caught.value.code == 0
    assert received_inputs == ["查看任务", "再试一次"]
    assert "AI: MCP 工具暂时不可用，请稍后重试。" in output
    assert "AI: 这是重试后的正常回答。" in output
