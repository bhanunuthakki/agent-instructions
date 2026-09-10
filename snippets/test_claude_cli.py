from __future__ import annotations

from types import SimpleNamespace

import claude_cli
import pytest


def test_default_membership_model_is_current_workhorse() -> None:
    assert claude_cli.DEFAULT_MODEL == "claude-sonnet-5"


def test_empty_output_raises_safe_execution_error(monkeypatch) -> None:
    marker = "do-not-expose-this-token"
    monkeypatch.setattr(claude_cli, "_verify_setup_once", lambda: None)
    monkeypatch.setattr(claude_cli, "_claude_cli_path", "/synthetic/claude")
    monkeypatch.setattr(
        claude_cli.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(stdout="", stderr=marker),
    )

    with pytest.raises(claude_cli.ClaudeExecutionError) as exc_info:
        claude_cli.call_claude("prompt")

    assert marker not in str(exc_info.value)
