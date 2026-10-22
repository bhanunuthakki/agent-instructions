from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path
import subprocess
import sys
import time

import claude_cli
import pytest


@pytest.fixture
def configured_cli(monkeypatch):
    monkeypatch.setattr(claude_cli, "_verify_setup_once", lambda: None)
    monkeypatch.setattr(claude_cli, "_claude_cli_path", "/synthetic/claude")


@pytest.mark.parametrize("tools", [None, ["WebSearch", "WebFetch"]])
def test_membership_call_exposes_only_explicit_web_tools(configured_cli, monkeypatch, tools):
    calls = []

    def run(argv, **kwargs):
        work = Path(kwargs["cwd"])
        assert work.is_dir() and not list(work.iterdir())
        calls.append((argv, work))
        return SimpleNamespace(stdout="answer", returncode=0)

    monkeypatch.setattr(claude_cli.subprocess, "run", run)
    assert claude_cli.call_claude("prompt", allowed_tools=tools) == "answer"
    argv, work = calls[0]
    for flag in ("--safe-mode", "--restricted", "--strict-mcp-config", "--no-session-persistence", "--disable-slash-commands"):
        assert flag in argv
    assert argv[argv.index("--tools") + 1] == ",".join(tools or [])
    assert argv[argv.index("--disallowedTools") + 1] == "mcp__*"
    assert not work.exists()


def test_membership_call_rejects_non_web_tool_before_dispatch(monkeypatch):
    monkeypatch.setattr(claude_cli, "_verify_setup_once", lambda: pytest.fail("must validate first"))
    with pytest.raises(ValueError, match="WebSearch|WebFetch"):
        claude_cli.call_claude("prompt", allowed_tools=["Read"])


def test_metered_credentials_are_rechecked_after_setup(monkeypatch):
    monkeypatch.setattr(claude_cli, "_setup_verified", True)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "synthetic-marker")
    with pytest.raises(RuntimeError):
        claude_cli._verify_setup_once()


def test_silent_stream_has_wall_clock_deadline_and_reaps_process(configured_cli, monkeypatch):
    real_popen = subprocess.Popen
    processes = []

    def fake_cli(argv, **kwargs):
        assert "--tools" in argv
        process = real_popen([sys.executable, "-c", "import time; time.sleep(30)"], **kwargs)
        processes.append((process, Path(kwargs["cwd"])))
        return process

    monkeypatch.setattr(claude_cli.subprocess, "Popen", fake_cli)
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        list(claude_cli.call_claude_stream("prompt", timeout_seconds=0.15))
    assert time.monotonic() - started < 5
    assert processes[0][0].poll() is not None
    assert not processes[0][1].exists()


def test_default_membership_model_is_current_workhorse() -> None:
    assert claude_cli.DEFAULT_MODEL == "claude-sonnet-5"


def test_empty_output_raises_safe_execution_error(monkeypatch) -> None:
    marker = "do-not-expose-this-token"
    monkeypatch.setattr(claude_cli, "_verify_setup_once", lambda: None)
    monkeypatch.setattr(claude_cli, "_claude_cli_path", "/synthetic/claude")
    monkeypatch.setattr(
        claude_cli.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(stdout="", stderr=marker, returncode=0),
    )

    with pytest.raises(claude_cli.ClaudeExecutionError) as exc_info:
        claude_cli.call_claude("prompt")

    assert marker not in str(exc_info.value)


def test_stream_success_and_consumer_close_reap_owned_process(configured_cli, monkeypatch):
    real_popen = subprocess.Popen
    processes = []
    event = '{"type":"stream_event","event":{"type":"content_block_delta","delta":{"type":"text_delta","text":"answer"}}}'

    def fake_cli(argv, **kwargs):
        program = f"import sys,time; sys.stdin.read(); print({event!r},flush=True); time.sleep(30)"
        process = real_popen([sys.executable, "-c", program], **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(claude_cli.subprocess, "Popen", fake_cli)
    stream = claude_cli.call_claude_stream("prompt", timeout_seconds=5)
    assert next(stream) == "answer"
    stream.close()
    assert processes[0].poll() is not None


def test_failed_membership_call_does_not_retain_sensitive_exception_context(configured_cli, monkeypatch):
    marker = "synthetic-private-content"
    monkeypatch.setattr(claude_cli.subprocess, "run", lambda *a, **k: SimpleNamespace(stdout=marker, stderr=marker, returncode=1))
    with pytest.raises(claude_cli.ClaudeExecutionError) as error:
        claude_cli.call_claude("prompt")
    assert marker not in str(error.value)
    assert error.value.__context__ is None
