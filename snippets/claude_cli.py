"""
claude_cli.py — Reusable wrapper for calling Claude from Python via the user's
Claude Pro/Max subscription (NOT the metered Anthropic API).

WHY THIS EXISTS
---------------
The `claude_agent_sdk` Python package and the Anthropic SDK both bill against
the metered Anthropic API (`ANTHROPIC_API_KEY`). The ONLY path to use a Claude
Code subscription from a Python script is to invoke the `claude` CLI as a
subprocess.

Three Windows-specific gotchas this wrapper handles:
  1. `subprocess.run(["claude", ...])` fails with FileNotFoundError on Windows
     because the npm-installed binary is `claude.CMD` and Python's subprocess
     doesn't apply PATHEXT to bare names. Fix: resolve the absolute path with
     shutil.which() at first call.
  2. `subprocess.run(input=str, text=True)` defaults to cp1252 on Windows and
     dies on financial/scientific Unicode (U+2212 minus, en/em dashes, arrows).
     Fix: force `encoding="utf-8"` and `errors="replace"`.
  3. Even with subscription auth set up, if `ANTHROPIC_API_KEY` is set in the
     environment, the CLI silently falls back to API billing. Fix: lazy check
     at first call, raise loudly with the unset instructions.

ONE-TIME SETUP (per machine)
----------------------------
1. Install Node.js (https://nodejs.org).
2. Install the CLI:
     npm install -g @anthropic-ai/claude-code
3. Authenticate to your subscription (browser flow):
     claude auth login
4. Verify:
     claude auth status     # should show your subscription account
     claude --version       # confirms binary is on PATH
5. Remove ANTHROPIC_API_KEY from your shell env / .env / shell profile.

USAGE
-----
    from claude_cli import call_claude
    response = call_claude("Summarize this in one sentence: " + text)

    # Token-by-token streaming variant (for interactive UIs):
    from claude_cli import call_claude_stream
    for chunk in call_claude_stream("Tell me a long story..."):
        print(chunk, end="", flush=True)

Or as a CLI test:
    python claude_cli.py "What is 2+2?"
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterator

# Keep the programmatic default on the current workhorse. Interactive orchestration uses
# Fable; bounded in-app calls should not silently spend the frontier tier.
DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_TIMEOUT_SECONDS = 600

_setup_verified: bool = False
_claude_cli_path: str | None = None


class ClaudeExecutionError(RuntimeError):
    """Claude CLI completed without a usable response."""


def _verify_setup_once() -> None:
    """Lazy environment check on first call — fails loud rather than mis-billing."""
    global _setup_verified, _claude_cli_path
    # Treat an empty-string value as unset. Claude Code's Bash tool leaks
    # ANTHROPIC_API_KEY='' into subshells even when the user has it unset, which
    # used to trip this guard as a false positive. Only a non-empty value would
    # actually route the CLI to API billing.
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        raise RuntimeError(
            "ANTHROPIC_API_KEY is set in the environment. The Claude Code CLI will silently "
            "route calls to API billing instead of your subscription. Unset it before running:\n"
            "  PowerShell:  Remove-Item env:ANTHROPIC_API_KEY\n"
            "  Bash:        unset ANTHROPIC_API_KEY"
        )
    if _setup_verified:
        return
    resolved = shutil.which("claude")
    if resolved is None:
        raise RuntimeError(
            "Claude Code CLI ('claude') not found in PATH. Install it with:\n"
            "  npm install -g @anthropic-ai/claude-code\n"
            "Then authenticate with: claude auth login"
        )
    _claude_cli_path = resolved
    _setup_verified = True


def _call_arguments(model: str, allowed_tools: list[str] | None = None) -> list[str]:
    tools = allowed_tools or []
    if any(tool not in {"WebSearch", "WebFetch"} for tool in tools):
        raise ValueError("Only explicit WebSearch and WebFetch tools are supported.")
    _verify_setup_once()
    assert _claude_cli_path is not None
    return [
        _claude_cli_path, "-p", "--model", model,
        "--safe-mode", "--restricted", "--disable-slash-commands",
        "--no-session-persistence", "--no-chrome",
        "--permission-mode", "dontAsk",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--disallowedTools", "mcp__*",
        "--settings", '{"disableAllHooks":true}',
        "--tools", ",".join(tools),
        *(["--allowedTools", ",".join(tools)] if tools else []),
    ]


def _stop_stream_process(proc: subprocess.Popen) -> None:
    """Stop the owned CLI process group; the caller reaps the parent."""
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        elif proc.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False, timeout=5,
            )
    except ProcessLookupError:
        pass


def call_claude(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    allowed_tools: list[str] | None = None,
) -> str:
    """Answer through subscription auth with no project context or tools by default.

    Opt into WebSearch/WebFetch only through allowed_tools. Calls use an empty
    temporary working directory and disable discovered customizations, MCP and
    session persistence. Managed administrator policy still applies; CLI controls
    are not an operating-system sandbox. Prompts stay on stdin and raw failures
    are not included in public exceptions.
    """
    argv = _call_arguments(model, allowed_tools)
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    with tempfile.TemporaryDirectory(prefix="claude-answer-") as working:
        timed_out = False
        try:
            result = subprocess.run(
                argv, input=prompt, cwd=working, capture_output=True,
                text=True, encoding="utf-8", errors="replace",
                check=False, timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            timed_out = True
        if timed_out:
            raise subprocess.TimeoutExpired("claude membership call", timeout_seconds)
        if result.returncode != 0:
            raise ClaudeExecutionError("Claude membership call failed.")
    text = result.stdout.strip()
    if not text:
        raise ClaudeExecutionError("Claude membership call returned empty output.")
    return text


def call_claude_stream(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Iterator[str]:
    """Stream answer text with a deadline covering input, reads, and process exit.

    Closing the iterator stops and reaps the owned subprocess. No tool-enabled
    streaming route is offered. Stderr is discarded rather than retained.
    """
    argv = _call_arguments(model) + [
        "--output-format", "stream-json", "--include-partial-messages", "--verbose",
    ]
    with tempfile.TemporaryDirectory(prefix="claude-stream-") as working:
        yield from _stream_in_directory(argv, prompt, timeout_seconds, working)


def _stream_in_directory(
    argv: list[str], prompt: str, timeout_seconds: int, working: str,
) -> Iterator[str]:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    proc = subprocess.Popen(
        argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
        bufsize=1, cwd=working, start_new_session=os.name == "posix",
    )
    expired = threading.Event()

    def expire() -> None:
        expired.set()
        _stop_stream_process(proc)

    timer = threading.Timer(timeout_seconds, expire)
    timer.daemon = True
    timer.start()
    try:
        assert proc.stdin is not None
        proc.stdin.write(prompt)
        proc.stdin.close()
        assert proc.stdout is not None
        for raw_line in proc.stdout:
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict) or event.get("type") != "stream_event":
                continue
            inner = event.get("event")
            if not isinstance(inner, dict) or inner.get("type") != "content_block_delta":
                continue
            delta = inner.get("delta")
            if isinstance(delta, dict) and delta.get("type") == "text_delta":
                text = delta.get("text")
                if isinstance(text, str) and text:
                    yield text
        rc = proc.wait()
        if expired.is_set():
            raise subprocess.TimeoutExpired("claude membership stream", timeout_seconds)
        if rc != 0:
            raise ClaudeExecutionError(f"Claude membership streaming call failed with status {rc}.")
    except OSError:
        if expired.is_set():
            raise subprocess.TimeoutExpired("claude membership stream", timeout_seconds) from None
        raise ClaudeExecutionError("Claude membership stream failed.") from None
    finally:
        timer.cancel()
        timer.join()
        _stop_stream_process(proc)
        proc.wait()
        for pipe in (proc.stdin, proc.stdout):
            if pipe is not None and not pipe.closed:
                pipe.close()


if __name__ == "__main__":
    # CLI test entrypoint: `python claude_cli.py "your prompt here"`
    if len(sys.argv) < 2:
        print("Usage: python claude_cli.py <prompt>", file=sys.stderr)
        sys.exit(2)
    prompt = " ".join(sys.argv[1:])
    print(call_claude(prompt))
