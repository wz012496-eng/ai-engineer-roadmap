from types import SimpleNamespace

from ai_engineer_roadmap import llm


def test_summarize_messages_returns_updated_summary(monkeypatch):
    request = {}

    def fake_create(**kwargs):
        request.update(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="用户从 Android 开发转向 AI，正在做任务管理 Agent。"
                    )
                )
            ]
        )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    monkeypatch.setattr(llm, "client", fake_client)

    result = llm.summarize_messages(
        [{"role": "user", "content": "我正在用 Python 写任务管理 Agent。"}],
        existing_summary="用户从 Android 开发转向 AI。",
    )

    assert result == "用户从 Android 开发转向 AI，正在做任务管理 Agent。"
    assert request["model"] == "deepseek-v4-flash"
    assert "用户从 Android 开发转向 AI。" in request["messages"][1]["content"]
    assert "任务管理 Agent" in request["messages"][1]["content"]


def test_log_context_trace_is_silent_when_disabled(monkeypatch, capsys):
    monkeypatch.delenv("AI_AGENT_CONTEXT_TRACE", raising=False)

    llm._log_context_trace(
        "trace-1",
        2,
        [{"role": "user", "content": "hello"}],
    )

    assert capsys.readouterr().out == ""


def test_log_context_trace_supports_dict_and_sdk_messages(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("AI_AGENT_CONTEXT_TRACE", "1")

    sdk_message = SimpleNamespace(
        role="assistant",
        content=None,
        tool_calls=[
            SimpleNamespace(
                id="call-1",
                function=SimpleNamespace(name="get_tasks", arguments="{}"),
            )
        ],
    )
    messages = [
        {"role": "user", "content": "有哪些任务？"},
        sdk_message,
    ]

    llm._log_context_trace("trace-2", 2, messages)

    output = capsys.readouterr().out
    assert "trace_id=trace-2 step=2 messages=2 content_chars=6" in output
    assert "role=assistant content_chars=0" in output
    assert "get_tasks" in output
