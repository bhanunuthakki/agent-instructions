from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path

import pytest

import linear_cli


class _Response:
    def __init__(self, payload: object) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_workspace_credential_precedes_global_fallback(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".env").write_text("LINEAR_API_KEY=workspace-key\n", encoding="utf-8")
    global_env = tmp_path / "global.env"
    global_env.write_text("LINEAR_API_KEY=global-key\n", encoding="utf-8")
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(linear_cli, "GLOBAL_ENV_PATH", global_env)

    assert linear_cli.resolve_api_key() == "workspace-key"


def test_process_credential_remains_the_explicit_override(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / ".env").write_text("LINEAR_API_KEY=workspace-key\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINEAR_API_KEY", "process-key")

    assert linear_cli.resolve_api_key() == "process-key"


def test_graphql_error_payload_is_not_exposed(monkeypatch) -> None:
    marker = "do-not-expose-this-token"
    monkeypatch.setattr(
        linear_cli.urllib.request,
        "urlopen",
        lambda request: _Response({"errors": [{"message": marker}]}),
    )

    with pytest.raises(linear_cli.LinearGraphQLError) as exc_info:
        linear_cli.LinearClient("synthetic-key").query("query { viewer { id } }")

    assert marker not in str(exc_info.value)


def test_null_graphql_data_is_not_treated_as_not_found(monkeypatch) -> None:
    monkeypatch.setattr(
        linear_cli.urllib.request,
        "urlopen",
        lambda request: _Response({"data": None}),
    )

    with pytest.raises(linear_cli.LinearClientError, match="invalid data envelope"):
        linear_cli.LinearClient("synthetic-key").get_issue("BHA-404")


def test_http_error_is_sanitized_and_suppresses_cause(monkeypatch) -> None:
    marker = "do-not-expose-this-token"

    def fail(_request: object) -> _Response:
        raise urllib.error.HTTPError(
            f"https://example.invalid/?api_key={marker}",
            401,
            marker,
            {},
            io.BytesIO(),
        )

    monkeypatch.setattr(linear_cli.urllib.request, "urlopen", fail)

    with pytest.raises(linear_cli.LinearTransportError) as exc_info:
        linear_cli.LinearClient("synthetic-key").query("query { viewer { id } }")

    assert marker not in str(exc_info.value)
    assert exc_info.value.__cause__ is None


def test_get_issue_propagates_transport_failure(monkeypatch) -> None:
    client = linear_cli.LinearClient("synthetic-key")

    def fail(_query: str, _variables: dict[str, object]) -> dict[str, object]:
        raise linear_cli.LinearTransportError("safe failure")

    monkeypatch.setattr(client, "query", fail)

    with pytest.raises(linear_cli.LinearTransportError):
        client.get_issue("BHA-404")
