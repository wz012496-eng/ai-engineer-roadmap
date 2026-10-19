from ai_engineer_roadmap import mcp_server
from ai_engineer_roadmap.mcp_server import (
    complete_task,
    create_task,
    write_permission_error,
)


def test_write_permission_is_denied_by_default(monkeypatch):
    # Ensure the environment variable is not set
    monkeypatch.delenv("MCP_ALLOW_WRITES", raising=False)

    result = write_permission_error()
    assert result is not None
    assert result["success"] is False
    assert result["error_type"] == "PERMISSION_DENIED"


def test_write_permission_is_allowed_when_explicitly_enabled(monkeypatch):
    # Set the environment variable to allow writes
    monkeypatch.setenv("MCP_ALLOW_WRITES", "1")

    result = write_permission_error()
    assert result is None


def test_create_task_does_not_execute_when_writes_are_disabled(
    monkeypatch,
):
    monkeypatch.delenv("MCP_ALLOW_WRITES", raising=False)

    def unexpected_create(*args, **kwargs):
        raise AssertionError("Write operation must not execute")

    monkeypatch.setattr(
        mcp_server,
        "run_create_task_tool",
        unexpected_create,
    )

    result = create_task("Review MCP", "high")

    assert result["success"] is False
    assert result["error_type"] == "PERMISSION_DENIED"


def test_complete_task_does_not_execute_when_writes_are_disabled(
    monkeypatch,
):
    monkeypatch.delenv("MCP_ALLOW_WRITES", raising=False)

    def unexpected_complete(*args, **kwargs):
        raise AssertionError("Write operation must not execute")

    monkeypatch.setattr(
        mcp_server,
        "run_complete_task_tool",
        unexpected_complete,
    )

    result = complete_task(1)

    assert result["success"] is False
    assert result["error_type"] == "PERMISSION_DENIED"
