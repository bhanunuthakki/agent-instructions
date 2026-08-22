"""Tests for the ChatGPT-membership Codex CLI transport."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import codex_cli


def _event_stream(text: str = "The answer") -> str:
    events = [
        {
            "type": "item.completed",
            "item": {"type": "agent_message", "text": text},
        },
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 120,
                "cached_input_tokens": 20,
                "output_tokens": 15,
                "reasoning_output_tokens": 4,
            },
        },
    ]
    return "\n".join(json.dumps(event) for event in events)


@pytest.fixture(autouse=True)
def reset_setup_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(codex_cli, "_setup_verified", False)
    monkeypatch.setattr(codex_cli, "_codex_cli_path", None)


def test_transport_source_has_no_machine_bound_windows_install_path() -> None:
    source = Path(codex_cli.__file__).read_text(encoding="utf-8")

    assert "C:" not in source
    assert "npm.cmd" not in source
    assert '"codex.cmd login"' not in source


@pytest.mark.parametrize("key", ["OPENAI_API_KEY", "CODEX_API_KEY"])
def test_setup_rejects_metered_api_credentials(
    monkeypatch: pytest.MonkeyPatch,
    key: str,
) -> None:
    monkeypatch.setenv(key, "present-but-never-logged")

    with pytest.raises(RuntimeError):
        codex_cli._verify_setup_once()


def test_api_key_guard_runs_after_setup_is_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(codex_cli, "_setup_verified", True)
    monkeypatch.setenv("OPENAI_API_KEY", "present-but-never-logged")

    with pytest.raises(RuntimeError):
        codex_cli._verify_setup_once()


def test_setup_prefers_the_managed_local_cli(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cli = tmp_path / "codex.cmd"
    cli.touch()
    monkeypatch.setattr(codex_cli, "MANAGED_CODEX_CLI", cli)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    completed = subprocess.CompletedProcess(
        args=[str(cli), "login", "status"],
        returncode=0,
        stdout="",
        stderr="Logged in using ChatGPT",
    )
    monkeypatch.setattr(codex_cli.subprocess, "run", lambda *args, **kwargs: completed)

    codex_cli._verify_setup_once()

    assert codex_cli._codex_cli_path == str(cli)


def test_exec_arguments_disable_agent_tools_and_persistence() -> None:
    argv = codex_cli._build_exec_argv(
        cli_path="codex.cmd",
        model="gpt-5.6-terra",
        reasoning_effort="medium",
        working_directory=Path("C:/tmp/isolated"),
    )

    assert argv[0:2] == ["codex.cmd", "exec"]
    assert "--ephemeral" in argv
    assert "--ignore-user-config" not in argv
    assert "--ignore-rules" in argv
    assert ["--sandbox", "read-only"] == argv[
        argv.index("--sandbox") : argv.index("--sandbox") + 2
    ]
    assert "shell_tool" in argv
    assert 'web_search="disabled"' in argv
    assert argv[-1] == "-"


def test_call_returns_validated_text_and_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    monkeypatch.setattr(codex_cli, "_verify_setup_once", lambda: None)
    monkeypatch.setattr(codex_cli, "_codex_cli_path", "codex.cmd")
    captured: dict[str, object] = {}

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["argv"] = argv
        captured.update(kwargs)
        return subprocess.CompletedProcess(argv, 0, _event_stream(), "")

    monkeypatch.setattr(codex_cli.subprocess, "run", fake_run)

    result = codex_cli.call_codex_with_usage("Explain the result")

    assert result.text == "The answer"
    assert result.usage.input_tokens == 120
    assert result.usage.cached_input_tokens == 20
    assert result.usage.output_tokens == 15
    assert result.usage.reasoning_output_tokens == 4
    assert captured["input"] == "Explain the result"
    assert captured["encoding"] == "utf-8"
    assert captured["check"] is True


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        json.dumps({"type": "turn.completed", "usage": {}}),
        json.dumps({"type": "item.completed", "item": {"type": "agent_message"}}),
        "not-json",
    ],
)
def test_event_stream_validation_fails_loudly(stdout: str) -> None:
    with pytest.raises(codex_cli.CodexEventError):
        codex_cli._parse_exec_events(stdout)


def test_cli_entrypoint_prints_the_transport_result(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(codex_cli, "call_codex", lambda prompt: f"reply:{prompt}")

    assert codex_cli.main(["hello", "world"]) == 0
    assert capsys.readouterr().out == "reply:hello world\n"


def test_cli_entrypoint_requires_a_prompt(capsys: pytest.CaptureFixture[str]) -> None:
    assert codex_cli.main([]) == 2
    assert "Usage:" in capsys.readouterr().err
