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
import subprocess
import sys
import threading
from collections.abc import Iterator

# Keep the programmatic default on the current workhorse. Interactive orchestration uses
# Fable; bounded in-app calls should not silently spend the frontier tier.
DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_TIMEOUT_SECONDS = 600

_setup_verified: bool = False
_claude_cli_path: str | None = None


def _verify_setup_once() -> None:
    """Lazy environment check on first call — fails loud rather than mis-billing."""
    global _setup_verified, _claude_cli_path
    if _setup_verified:
        return
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
    resolved = shutil.which("claude")
    if resolved is None:
        raise RuntimeError(
            "Claude Code CLI ('claude') not found in PATH. Install it with:\n"
            "  npm install -g @anthropic-ai/claude-code\n"
            "Then authenticate with: claude auth login"
        )
    _claude_cli_path = resolved
    _setup_verified = True


def call_claude(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    allowed_tools: list[str] | None = None,
) -> str:
    """
    Single-shot LLM call via the Claude Code CLI. Returns the model's text response.

    Prompts are passed via stdin to avoid the Windows CreateProcess command-line
    length limit (32K). Output is decoded as UTF-8 with error replacement so bad
    bytes from upstream sources (e.g., PDF extraction) don't crash the call.

    allowed_tools: optional list of Claude Code tool names to enable for this headless
      call (e.g. ["WebSearch", "WebFetch"]). In -p mode tools are otherwise unavailable,
      so this is required for any call that must research the web. Passed as a single
      space-separated --allowedTools argument.

    Raises:
      RuntimeError: setup is wrong (CLI not installed, or ANTHROPIC_API_KEY set).
      subprocess.CalledProcessError: CLI returned non-zero exit; stderr in .stderr.
      subprocess.TimeoutExpired: prompt didn't finish within timeout_seconds.
    """
    _verify_setup_once()
    assert _claude_cli_path is not None
    argv = [_claude_cli_path, "-p", "--model", model]
    if allowed_tools:
        argv += ["--allowedTools", " ".join(allowed_tools)]
    result = subprocess.run(
        argv,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=timeout_seconds,
    )
    text = result.stdout.strip()
    if not text:
        raise RuntimeError(f"claude -p returned empty stdout. stderr: {result.stderr.strip()}")
    return text


def call_claude_stream(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Iterator[str]:
    """
    Streaming variant of `call_claude`. Yields text chunks (deltas) as the
    model produces them, suitable for piping into Server-Sent Events or
    any other token-by-token UI.

    Uses `claude -p --output-format stream-json --include-partial-messages
    --verbose`, which emits one JSON event per line. We filter for
    `stream_event` → `content_block_delta` → `text_delta` events; any
    extended-thinking deltas are ignored (the user doesn't want to see
    them in chat). The full assistant text is just the concatenation of
    yielded chunks.

    Stderr is drained on a background thread to avoid the child blocking
    if the buffer fills (the CLI emits a few status lines + occasional
    warnings). A non-zero exit code surfaces as RuntimeError with the
    drained stderr attached.

    Raises:
      RuntimeError: setup is wrong (CLI not installed, or ANTHROPIC_API_KEY set),
        or the CLI exited non-zero. Stderr is in the message.
      subprocess.TimeoutExpired: process didn't exit within timeout_seconds.
    """
    _verify_setup_once()
    assert _claude_cli_path is not None
    proc = subprocess.Popen(
        [
            _claude_cli_path,
            "-p",
            "--model", model,
            "--output-format", "stream-json",
            "--include-partial-messages",
            "--verbose",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,  # line-buffered so we get JSON events as they arrive
    )

    # Drain stderr on a background thread. Without this the child can
    # deadlock if the pipe fills before we read it; with it we have the
    # full stderr available for any error message.
    stderr_buf: list[str] = []

    def _drain_stderr() -> None:
        assert proc.stderr is not None
        for line in proc.stderr:
            stderr_buf.append(line)

    stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
    stderr_thread.start()

    try:
        assert proc.stdin is not None
        proc.stdin.write(prompt)
        proc.stdin.close()

        assert proc.stdout is not None
        for raw_line in proc.stdout:
            line = raw_line.rstrip("\r\n")
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                # The CLI shouldn't emit non-JSON on stdout in stream-json
                # mode, but if it ever does, skipping is safer than crashing.
                continue
            if ev.get("type") != "stream_event":
                continue
            inner = ev.get("event") or {}
            if inner.get("type") != "content_block_delta":
                continue
            delta = inner.get("delta") or {}
            # Skip thinking_delta — we don't surface extended thinking to the user.
            if delta.get("type") != "text_delta":
                continue
            text = delta.get("text") or ""
            if text:
                yield text

        rc = proc.wait(timeout=timeout_seconds)
        stderr_thread.join(timeout=5)
        if rc != 0:
            stderr_text = "".join(stderr_buf).strip()
            raise RuntimeError(
                f"claude -p (stream-json) exited {rc}. stderr: {stderr_text[:1000]}"
            )
    except GeneratorExit:
        # Consumer closed the generator early (e.g. client disconnected).
        # Kill the subprocess so it doesn't run to completion in the background.
        proc.kill()
        raise
    except BaseException:
        proc.kill()
        raise


if __name__ == "__main__":
    # CLI test entrypoint: `python claude_cli.py "your prompt here"`
    if len(sys.argv) < 2:
        print("Usage: python claude_cli.py <prompt>", file=sys.stderr)
        sys.exit(2)
    prompt = " ".join(sys.argv[1:])
    print(call_claude(prompt))
