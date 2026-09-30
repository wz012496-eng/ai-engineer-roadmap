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
