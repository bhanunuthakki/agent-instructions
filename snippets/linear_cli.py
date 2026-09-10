"""linear_cli.py — Reusable, zero-dependency client and CLI for Linear across Antigravity projects.

Resolves LINEAR_API_KEY from:
  1. os.environ['LINEAR_API_KEY']
  2. Current workspace .env or secrets/linear/api_key.txt
  3. /Applications/agent-instructions/.env

Usage from Python:
    from snippets.linear_cli import LinearClient
    client = LinearClient()
    viewer = client.get_viewer()
    issue = client.get_issue('BHA-124')

Usage from Shell:
    python snippets/linear_cli.py whoami
    python snippets/linear_cli.py teams
    python snippets/linear_cli.py projects
    python snippets/linear_cli.py issues BHA
    python snippets/linear_cli.py get BHA-124
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
GLOBAL_ENV_PATH = Path("/Applications/agent-instructions/.env")


class LinearClientError(RuntimeError):
    """Safe public base error for Linear client failures."""


class LinearGraphQLError(LinearClientError):
    """Linear returned a GraphQL error without exposing its raw payload."""


class LinearTransportError(LinearClientError):
    """The Linear request failed before a valid GraphQL response arrived."""


def _key_from_file(path: Path) -> str:
    if not path.is_file():
        return ""
    if path.name != ".env" and path.suffix != ".env":
        return path.read_text(encoding="utf-8").strip()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, value = line.partition("=")
        if separator and name.strip() == "LINEAR_API_KEY":
            return value.strip().strip("\"'")
    return ""


def resolve_api_key() -> str:
    """Resolves Linear API key without logging or printing secret values."""
    env_val = os.environ.get("LINEAR_API_KEY", "").strip()
    if env_val:
        return env_val

    # A workspace-local credential is narrower than the shared Mac fallback.
    cwd = Path.cwd()
    candidates = [
        cwd / ".env",
        cwd / "secrets" / "linear" / "api_key.txt",
        cwd / "secrets" / "linear" / "token.txt",
    ]
    for candidate in candidates:
        value = _key_from_file(candidate)
        if value:
            return value

    value = _key_from_file(GLOBAL_ENV_PATH)
    if value:
        return value

    return ""


class LinearClient:
    """Zero-dependency GraphQL client for Linear API."""

    def __init__(self, api_key: str | None = None) -> None:
        resolved = api_key or resolve_api_key()
        if not resolved:
            raise ValueError(
                "LINEAR_API_KEY could not be resolved. "
                "Set LINEAR_API_KEY or configure /Applications/agent-instructions/.env"
            )
        self._api_key = resolved

    def query(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data = json.dumps({"query": query, "variables": variables or {}}).encode(
            "utf-8"
        )
        req = urllib.request.Request(
            LINEAR_GRAPHQL_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": self._api_key,
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                try:
                    res = json.loads(resp.read().decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    raise LinearClientError("Linear returned an invalid JSON response.") from None
                if not isinstance(res, dict):
                    raise LinearClientError("Linear returned an invalid response envelope.")
                if res.get("errors"):
                    raise LinearGraphQLError("Linear GraphQL request failed.")
                result = res.get("data")
                if not isinstance(result, dict):
                    raise LinearClientError("Linear returned an invalid data envelope.")
                return result
        except urllib.error.HTTPError as exc:
            raise LinearTransportError(
                f"Linear HTTP request failed with status {exc.code}."
            ) from None
        except urllib.error.URLError:
            raise LinearTransportError("Linear request could not reach the service.") from None

    def get_viewer(self) -> dict[str, Any]:
        data = self.query("query { viewer { id name email } }")
        return data.get("viewer", {})

    def list_teams(self) -> list[dict[str, Any]]:
        data = self.query("query { teams { nodes { id name key } } }")
        return data.get("teams", {}).get("nodes", [])

    def list_projects(self, team_id: str | None = None) -> list[dict[str, Any]]:
        if team_id:
            query = """
            query($teamId: String!) {
              team(id: $teamId) { projects { nodes { id name state } } }
            }
            """
            data = self.query(query, {"teamId": team_id})
            return data.get("team", {}).get("projects", {}).get("nodes", [])
        data = self.query("query { projects { nodes { id name state } } }")
        return data.get("projects", {}).get("nodes", [])

    def get_issue(self, issue_key: str) -> dict[str, Any] | None:
        query = """
        query($id: String!) {
          issue(id: $id) {
            id identifier title description priority estimate url
            state { id name }
            project { id name }
            labels { nodes { id name } }
          }
        }
        """
        data = self.query(query, {"id": issue_key})
        return data.get("issue")

    def list_issues(self, team_key: str, limit: int = 50) -> list[dict[str, Any]]:
        query = """
        query($teamKey: String!, $limit: Int!) {
          issues(filter: { team: { key: { eq: $teamKey } } }, first: $limit) {
            nodes {
              id identifier title priority estimate url
              state { name }
              project { name }
            }
          }
        }
        """
        data = self.query(query, {"teamKey": team_key, "limit": limit})
        return data.get("issues", {}).get("nodes", [])

    def create_issue(
        self,
        team_id: str,
        title: str,
        description: str = "",
        priority: int = 0,
        estimate: int | None = None,
        project_id: str | None = None,
        label_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        mutation = """
        mutation($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier title url }
          }
        }
        """
        input_data: dict[str, Any] = {
            "teamId": team_id,
            "title": title,
            "description": description,
            "priority": priority,
        }
        if estimate is not None:
            input_data["estimate"] = estimate
        if project_id:
            input_data["projectId"] = project_id
        if label_ids:
            input_data["labelIds"] = label_ids

        data = self.query(mutation, {"input": input_data})
        return data.get("issueCreate", {}).get("issue", {})


def main() -> None:
    parser = argparse.ArgumentParser(description="Linear API CLI for Antigravity")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("whoami", help="Check authenticated viewer")
    subparsers.add_parser("teams", help="List accessible teams")
    subparsers.add_parser("projects", help="List all projects")

    issues_p = subparsers.add_parser("issues", help="List issues for a team")
    issues_p.add_argument("team_key", help="Team key (e.g. BHA, HUNT)")
    issues_p.add_argument("--limit", type=int, default=30, help="Limit results")

    get_p = subparsers.add_parser("get", help="Get single issue details")
    get_p.add_argument("issue_key", help="Issue key (e.g. BHA-124)")

    args = parser.parse_args()

    client = LinearClient()

    if args.command == "whoami":
        viewer = client.get_viewer()
        print(f"Logged in as: {viewer.get('name')} ({viewer.get('email')})")

    elif args.command == "teams":
        teams = client.list_teams()
        print(f"{'Key':<8} | {'Name':<25} | {'ID'}")
        print("-" * 70)
        for t in teams:
            print(f"{t.get('key'):<8} | {t.get('name'):<25} | {t.get('id')}")

    elif args.command == "projects":
        projects = client.list_projects()
        print(f"{'Project Name':<40} | {'State':<12} | {'ID'}")
        print("-" * 75)
        for p in projects:
            print(
                f"{p.get('name', ''):<40} | {p.get('state', ''):<12} | {p.get('id')}"
            )

    elif args.command == "issues":
        issues = client.list_issues(args.team_key, limit=args.limit)
        print(f"{'Key':<10} | {'Project':<30} | {'State':<12} | {'Title'}")
        print("-" * 85)
        for i in issues:
            proj = (i.get("project") or {}).get("name", "—")
            state = (i.get("state") or {}).get("name", "—")
            print(
                f"{i.get('identifier'):<10} | {proj[:28]:<30} | {state:<12} | {i.get('title')}"
            )

    elif args.command == "get":
        issue = client.get_issue(args.issue_key)
        if not issue:
            print(f"Issue {args.issue_key} not found.")
            sys.exit(1)
        print(json.dumps(issue, indent=2))


if __name__ == "__main__":
    main()
