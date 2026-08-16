"""ChatGPT-membership transport for governed Python LLM calls.

This module invokes the official Codex CLI as an isolated, non-interactive
subprocess. It never uses the OpenAI SDK or API-key authentication. The managed
CLI and its dedicated authentication home live beside this shared snippet tree.

One-time setup from the agent-instructions clone::

    npm install --prefix .tools @openai/codex
    CODEX_HOME=.codex-membership .tools/node_modules/.bin/codex login

Choose "Sign in with ChatGPT" in the browser flow. Do not use ``--with-api-key``.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping, TypeAlias, get_args

ReasoningEffort: TypeAlias = Literal[
    "none",
    "low",
    "medium",
    "high",
    "xhigh",
    "max",
]

# Codex's `web_search` config is a MODE, not a boolean — the CLI rejects any
# other value at config-load time (verified 2026-08-03: passing "enabled"
# exits 1 with `unknown variant`, listing exactly these four). "disabled" is
# this wrapper's default and the isolation posture every caller inherits.
WebSearchMode: TypeAlias = Literal[
    "disabled",
    "cached",
    "indexed",
    "live",
]

DEFAULT_MODEL = "gpt-5.6-terra"
DEFAULT_REASONING_EFFORT: ReasoningEffort = "medium"
DEFAULT_WEB_SEARCH: WebSearchMode = "disabled"
DEFAULT_TIMEOUT_SECONDS = 600
CHATGPT_LOGIN_STATUS = "Logged in using ChatGPT"

_WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
_MANAGED_CODEX_NAME = "codex.cmd" if os.name == "nt" else "codex"
MANAGED_CODEX_CLI = (
    _WORKSPACE_ROOT / ".tools" / "node_modules" / ".bin" / _MANAGED_CODEX_NAME
)
MEMBERSHIP_CODEX_HOME = _WORKSPACE_ROOT / ".codex-membership"
METERED_CREDENTIAL_KEYS = ("OPENAI_API_KEY", "CODEX_API_KEY")

_setup_verified = False
_codex_cli_path: str | None = None


class CodexEventError(RuntimeError):
    """The Codex JSONL stream did not match the required event schema."""


class CodexExecutionError(RuntimeError):
    """The Codex subprocess failed without exposing its potentially sensitive output."""


@dataclass(frozen=True)
class CodexUsage:
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int


@dataclass(frozen=True)
class CodexResult:
    text: str
    usage: CodexUsage


def _membership_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in METERED_CREDENTIAL_KEYS:
        env.pop(key, None)
    env["CODEX_HOME"] = str(MEMBERSHIP_CODEX_HOME)
    env["NO_COLOR"] = "1"
    return env


def _resolve_cli() -> str:
    if MANAGED_CODEX_CLI.is_file():
        return str(MANAGED_CODEX_CLI)
    resolved = shutil.which("codex")
    if resolved is None:
        raise RuntimeError(
            "Codex CLI is not installed. Install the managed copy with: "
            f"npm install --prefix {_WORKSPACE_ROOT / '.tools'} @openai/codex"
        )
    return resolved


def _verify_setup_once() -> None:
    """Verify a dedicated ChatGPT login and reject every API-key path."""
    global _setup_verified, _codex_cli_path
    configured_keys = [
        key for key in METERED_CREDENTIAL_KEYS if os.environ.get(key, "").strip()
    ]
    if configured_keys:
        raise RuntimeError(
            "Metered OpenAI credentials are present. Unset OPENAI_API_KEY and "
            "CODEX_API_KEY before using the membership transport."
        )
    if _setup_verified:
        return

    cli_path = _resolve_cli()
    try:
        status = subprocess.run(
            [cli_path, "login", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
            env=_membership_env(),
        )
    except (OSError, subprocess.TimeoutExpired):
        raise RuntimeError(
            "Codex membership authentication could not be verified."
        ) from None

    status_values = (status.stdout.strip(), status.stderr.strip())
    if status.returncode != 0 or CHATGPT_LOGIN_STATUS not in status_values:
        raise RuntimeError(
            "The dedicated Codex home is not signed in with ChatGPT. Set CODEX_HOME to "
            f"{MEMBERSHIP_CODEX_HOME} and run '{cli_path} login'."
        )
    _codex_cli_path = cli_path
    _setup_verified = True


def _build_exec_argv(
    *,
    cli_path: str,
    model: str,
    reasoning_effort: ReasoningEffort,
    working_directory: Path,
    web_search: WebSearchMode = DEFAULT_WEB_SEARCH,
) -> list[str]:
    if not model.startswith("gpt-"):
        raise ValueError(
            "The membership Codex transport accepts only OpenAI GPT model IDs."
        )
    return [
        cli_path,
        "exec",
        "--model",
        model,
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--color",
        "never",
        "--json",
        "--disable",
        "shell_tool",
        "--disable",
        "shell_snapshot",
        "--disable",
        "apps",
        "--disable",
        "hooks",
        "--disable",
        "multi_agent",
        "--disable",
        "remote_plugin",
        "--config",
        f'web_search="{web_search}"',
        "--config",
        f'model_reasoning_effort="{reasoning_effort}"',
        "--cd",
        str(working_directory),
        "-",
    ]


def _as_mapping(value: object, *, event_name: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CodexEventError(f"{event_name} must be a JSON object with string keys.")
    return value


def _token_count(usage: Mapping[str, object], field: str) -> int:
    value = usage.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise CodexEventError(
            f"turn.completed usage.{field} must be a non-negative integer."
        )
    return value


def _parse_exec_events(stdout: str) -> CodexResult:
    final_text: str | None = None
    final_usage: CodexUsage | None = None
    if not stdout.strip():
        raise CodexEventError("Codex returned an empty event stream.")

    for raw_line in stdout.splitlines():
        if not raw_line.strip():
            continue
        try:
            decoded: object = json.loads(raw_line)
        except json.JSONDecodeError:
            raise CodexEventError("Codex returned a non-JSON event.") from None
        event = _as_mapping(decoded, event_name="event")
        event_type = event.get("type")

        if event_type == "item.completed":
            item = _as_mapping(event.get("item"), event_name="item.completed.item")
            if item.get("type") == "agent_message":
                text = item.get("text")
                if not isinstance(text, str) or not text.strip():
                    raise CodexEventError(
                        "item.completed agent_message.text must be a non-empty string."
                    )
                final_text = text.strip()
        elif event_type == "turn.completed":
            usage = _as_mapping(event.get("usage"), event_name="turn.completed.usage")
            final_usage = CodexUsage(
                input_tokens=_token_count(usage, "input_tokens"),
                cached_input_tokens=_token_count(usage, "cached_input_tokens"),
                output_tokens=_token_count(usage, "output_tokens"),
                reasoning_output_tokens=_token_count(usage, "reasoning_output_tokens"),
            )

    if final_text is None:
        raise CodexEventError("Codex did not return a final agent message.")
    if final_usage is None:
        raise CodexEventError("Codex did not return token usage.")
    return CodexResult(text=final_text, usage=final_usage)


def call_codex_with_usage(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    reasoning_effort: ReasoningEffort = DEFAULT_REASONING_EFFORT,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    web_search: WebSearchMode = DEFAULT_WEB_SEARCH,
) -> CodexResult:
    """Return the final text and measured tokens from one isolated Codex call.

    ``web_search`` is OPT-IN and defaults to ``"disabled"``, so the isolation
    posture every existing caller relies on is unchanged. ``"live"`` grounds the
    answer in fresh sources; ``"cached"``/``"indexed"`` trade freshness for
    speed. Any non-``"disabled"`` mode admits fetched web content, which is
    UNTRUSTED input (indirect prompt injection). The rest of the isolation still
    holds — read-only sandbox, ephemeral home, empty working directory, and no
    shell, apps, hooks, multi-agent, or plugins — so a hostile page can
    influence the answer text but cannot reach the filesystem, the project, or
    another tool. Treat a web-grounded response as evidence to verify, never as
    an instruction, and prefer a longer ``timeout_seconds`` (fetches add
    round-trips).
    """
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    # Fail here, not 2s later inside the CLI's config loader with an opaque
    # `exited with status 1` (the wrapper deliberately swallows stderr).
    if web_search not in get_args(WebSearchMode):
        raise ValueError(
            f"web_search must be one of {get_args(WebSearchMode)}, got {web_search!r}"
        )
    _verify_setup_once()
    if _codex_cli_path is None:
        raise RuntimeError("Codex setup verification did not resolve an executable.")

    with tempfile.TemporaryDirectory(prefix="codex-llm-") as temp_dir:
        argv = _build_exec_argv(
            cli_path=_codex_cli_path,
            model=model,
            reasoning_effort=reasoning_effort,
            working_directory=Path(temp_dir),
            web_search=web_search,
        )
        try:
            completed = subprocess.run(
                argv,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                timeout=timeout_seconds,
                env=_membership_env(),
            )
        except subprocess.TimeoutExpired:
            raise CodexExecutionError("Codex membership call timed out.") from None
        except subprocess.CalledProcessError as exc:
            raise CodexExecutionError(
                f"Codex membership call exited with status {exc.returncode}."
            ) from None
        except OSError:
            raise CodexExecutionError(
                "Codex membership call could not start."
            ) from None
    return _parse_exec_events(completed.stdout)


def call_codex(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    reasoning_effort: ReasoningEffort = DEFAULT_REASONING_EFFORT,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    web_search: WebSearchMode = DEFAULT_WEB_SEARCH,
) -> str:
    """Return only the final text for callers whose ledger is handled elsewhere.

    See :func:`call_codex_with_usage` for the ``web_search`` opt-in contract.
    """
    return call_codex_with_usage(
        prompt,
        model=model,
        reasoning_effort=reasoning_effort,
        timeout_seconds=timeout_seconds,
        web_search=web_search,
    ).text
