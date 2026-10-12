from ai_engineer_roadmap.mcp_server import write_permission_error


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
