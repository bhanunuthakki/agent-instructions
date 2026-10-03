"""Tool-neutral workspace inventory and offline verification. Never loads secret files.

Install commands are documentation, never executed. Subprocess output is hashed,
not retained or emitted: a receipt cannot accidentally become a credential log.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "workspace_reconstruction.json"
MODES = {"fast", "full", "build"}
Status = Literal["pass", "fail", "skip"]


@dataclass(frozen=True)
class CheckReceipt:
    project: str
    check: str
    status: Status
    category: str
    reason: str
    exit_code: int | None = None
    duration_seconds: float = 0
    output_sha256: str | None = None


@dataclass
class WorkspaceReceipt:
    schema_version: int = 1
    manifest_sha256: str = ""
    mode: str = "fast"
    executed: bool = False
    clean_home: bool = False
    platform: str = sys.platform
    status: Status = "fail"
    scope: str = "workspace"
    declared_contract_ready: bool = False
    checks: list[CheckReceipt] = field(default_factory=list)
    inventory_errors: list[str] = field(default_factory=list)
    local_only_sources: list[str] = field(default_factory=list)


def mapping(value: object, location: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        raise ValueError(f"{location}: expected object")
    return cast("dict[str, object]", value)


def strings(value: object, location: str, *, empty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (not value and not empty)
        or any(not isinstance(v, str) or not v.strip() for v in value)
    ):
        raise ValueError(f"{location}: expected nonempty string list")
    return cast("list[str]", value)


def text(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location}: expected nonempty string")
    return value


def records(value: object, location: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location}: expected nonempty record list")
    return [mapping(v, location) for v in value]


def confined(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts or "\\" in relative:
        raise ValueError("path: expected confined portable relative path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("path: symlink escapes declared root")
    return path


def guide_projects(root: Path) -> set[str]:
    guide = (root / "AGENTS_GUIDE.md").read_text(encoding="utf-8")
    section = guide.split("<!-- BEGIN:projects -->", 1)[1].split(
        "<!-- END:projects -->", 1
    )[0]
    return {
        m.group(1)
        for m in re.finditer(r"^\| ([a-z][a-z0-9-]+) \|", section, re.MULTILINE)
        if m.group(1) != "Project"
    }


def validate(
    manifest: dict[str, object],
    workspace: Path,
    *,
    root: Path = ROOT,
    paths: bool = True,
) -> list[str]:
    """Reject structural omissions and stale code/doc paths, without opening state or secrets."""
    errors: list[str] = []
    try:
        if manifest.get("schema_version") != 1:
            raise ValueError("schema_version: expected1")
        for key in [
            "canonical_source",
            "population_authority",
            "population_note",
            "regeneration",
        ]:
            text(manifest.get(key), key)
        url = text(manifest.get("assessment_url"), "assessment_url")
        if not url.startswith("https://linear.app/") or "/document/" not in url:
            raise ValueError("assessment_url: durable Linear document required")
        projects = records(manifest.get("projects"), "projects")
        ids = [text(p.get("id"), "project.id") for p in projects]
        if len(ids) != len(set(ids)):
            errors.append("projects: duplicate identity")
        if set(ids) != guide_projects(root):
            errors.append(
                "projects: population differs from canonical AGENTS_GUIDE project census"
            )
        repos = [text(p.get("repo"), "project.repo") for p in projects]
        if len(repos) != len(set(repos)):
            errors.append("projects: duplicate repository location")
        usage = json.loads(
            (root / "config" / "llm_usage_index.json").read_text(encoding="utf-8")
        )
        registered = {p["project"]: p for p in usage["projects"]}
        for project in projects:
            name = text(project.get("id"), "project.id")
            if not re.fullmatch(r"[a-z][a-z0-9-]+", name):
                raise ValueError("project.id: invalid identity")
            repo_name = text(project.get("repo"), f"{name}.repo")
            if repo_name != name:
                raise ValueError(f"{name}: canonical repository identity mismatch")
            repo = confined(workspace, repo_name)
            refs: list[str] = []
            for key in ["documentation", "install_sources"]:
                refs.extend(strings(project.get(key), f"{name}.{key}"))
            for key in [
                "toolchain",
                "install",
                "scheduled_jobs",
                "state_boundaries",
                "secret_boundaries",
                "vendor_harness_coupling",
            ]:
                strings(project.get(key), f"{name}.{key}")
            for key in ["transition_recovery", "hook_ci_disposition"]:
                text(project.get(key), f"{name}.{key}")
            for direction in records(
                project.get("canonical_generated"), f"{name}.canonical_generated"
            ):
                refs.extend(strings(direction.get("canonical"), f"{name}.canonical"))
                strings(direction.get("generated"), f"{name}.generated")
                text(direction.get("regenerate"), f"{name}.regenerate")
            llm = mapping(project.get("llm"), f"{name}.llm")
            state = text(llm.get("status"), f"{name}.llm.status")
            if state not in {"registered", "migration_required", "not_applicable"}:
                raise ValueError(f"{name}.llm.status: invalid disposition")
            entries = strings(
                llm.get("entrypoints"),
                f"{name}.llm.entrypoints",
                empty=state == "not_applicable",
            )
            refs.extend(entries)
            refs.extend(
                strings(llm.get("adapters"), f"{name}.llm.adapters", empty=True)
            )
            for key in [
                "usage_index",
                "purpose_authority",
                "prompt_schema_versions",
                "ledger_authority",
                "eval_authority",
            ]:
                text(llm.get(key), f"{name}.llm.{key}")
            strings(
                llm.get("residual_inventory"),
                f"{name}.llm.residual_inventory",
                empty=state != "migration_required",
            )
            if name in registered and (
                state != "registered" or entries != [registered[name]["entrypoint"]]
            ):
                errors.append(
                    f"{name}: LLM entrypoint differs from canonical usage index"
                )
            check_ids: set[str] = set()
            modes: set[str] = set()
            for command in records(project.get("commands"), f"{name}.commands"):
                cid = text(command.get("id"), f"{name}.check.id")
                if cid in check_ids:
                    errors.append(f"{name}: duplicate check identity")
                check_ids.add(cid)
                selected = strings(command.get("modes"), f"{name}.{cid}.modes")
                if not set(selected) <= MODES:
                    raise ValueError(f"{name}.{cid}: invalid mode")
                modes.update(selected)
                if "builtin" in command:
                    if command["builtin"] not in ("python_syntax", "markdown_links"):
                        raise ValueError(f"{name}.{cid}: unknown builtin")
                    refs.extend(strings(command.get("paths"), f"{name}.{cid}.paths"))
                    text(command.get("reason"), f"{name}.{cid}.reason")
                else:
                    argv = strings(command.get("argv"), f"{name}.{cid}.argv")
                    if command.get("offline_safe") is not True:
                        raise ValueError(f"{name}.{cid}: offline review required")
                    if argv[0] not in (
                        "{python}",
                        "node",
                        "npm",
                        "gradle",
                        "sh",
                        "make",
                    ):
                        raise ValueError(f"{name}.{cid}: unsupported executable")
                    cwd = text(command.get("cwd"), f"{name}.{cid}.cwd")
                    if cwd != "@workspace":
                        confined(repo, cwd)
                    strings(
                        command.get("python_modules"),
                        f"{name}.{cid}.python_modules",
                        empty=True,
                    )
                    refs.extend(
                        strings(
                            command.get("source_paths"),
                            f"{name}.{cid}.source_paths",
                            empty=True,
                        )
                    )
                    timeout = command.get("timeout_seconds")
                    if type(timeout) is not int or not 1 <= timeout <= 3600:
                        raise ValueError(f"{name}.{cid}: invalid timeout")
            if not {"fast", "full"} <= modes:
                errors.append(f"{name}: missing fast/full contract")
            if "build" not in modes and name != "xr-glasses-dev-guide":
                errors.append(f"{name}: missing compile/build contract")
            for ref in refs:
                candidate = confined(repo, ref.partition(":")[0])
                if paths and not candidate.exists():
                    errors.append(f"{name}: missing source path {ref}")
            if paths and not (repo / ".git").exists():
                errors.append(f"{name}: repository version ownership missing")
    except (ValueError, KeyError, IndexError, OSError, TypeError):
        # Do not reflect untrusted JSON values or source bytes in diagnostics.
        errors.append(
            "manifest: malformed or incomplete required contract; inspect field structure locally"
        )
    return errors


def resolve_python(repo: Path, override: str | None) -> str | None:
    if override:
        return shutil.which(override)
    for relative in [
        ".venv/Scripts/python.exe",
        ".venv/bin/python",
        "venv/Scripts/python.exe",
        "venv/bin/python",
    ]:
        path = repo / relative
        if path.is_file():
            return str(path)
    return None


def source_readiness(
    project: dict[str, object], repo: Path, *, env: dict[str, str]
) -> list[str]:
    """Bind entrypoints and check authorities to committed source without listing private paths."""
    entries = list(
        strings(mapping(project["llm"], "llm")["entrypoints"], "entries", empty=True)
    )
    for command in records(project["commands"], "commands"):
        entries.extend(
            strings(
                command["paths"] if "builtin" in command else command["source_paths"],
                "command sources",
            )
        )
    result: list[str] = []
    for relative in sorted(set(entries)):
        check = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            env=env,
        )
        modified = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            env=env,
        )
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", relative],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            env=env,
        )
        if (
            check.returncode
            or modified.returncode
            or untracked.returncode
            or untracked.stdout
        ):
            result.append(f"{project['id']}:{relative}")
    return result


def builtin_check(repo: Path, command: dict[str, object]) -> tuple[bool, str]:
    kind = command["builtin"]
    errors = 0
    examined = 0
    for relative in strings(command["paths"], "paths"):
        path = confined(repo, relative)
        if not path.exists():
            errors += 1
            continue
        files = (
            [path]
            if path.is_file()
            else list(path.glob("*.md"))
            if kind == "markdown_links"
            else list(path.rglob("*.py"))
        )
        for file in files:
            if any(
                p in {".git", ".venv", "venv", "node_modules", ".tmp", "__pycache__"}
                for p in file.relative_to(repo).parts
            ):
                continue
            examined += 1
            try:
                # Resolve each enumerated file; a directory scan can find escaping links.
                safe_file = confined(repo, file.relative_to(repo).as_posix())
                content = safe_file.read_text(encoding="utf-8")
                if kind == "python_syntax":
                    ast.parse(content, filename=str(file))
                else:
                    for link in re.findall(r"\]\(([^)]+)\)", content):
                        target = link.strip("<>").split("#", 1)[0]
                        if (
                            target
                            and not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target)
                            and not target.startswith("/")
                            and not (file.parent / target).exists()
                        ):
                            errors += 1
            except (OSError, SyntaxError, UnicodeError, ValueError):
                errors += 1
    if examined == 0 and errors == 0:
        errors = 1
    return (
        errors == 0,
        f"{examined} source file(s) checked; {errors} syntax/local-link error(s); no imports, provider calls or bytecode writes",
    )


def bounded_process(
    argv: list[str], *, cwd: Path, env: dict[str, str], timeout: int
) -> tuple[int, bytes]:
    """Own the process group and terminate descendants on abnormal exit."""
    with subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=os.name != "nt",
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        if os.name == "nt"
        else 0,
    ) as process:
        try:
            output, _ = process.communicate(timeout=timeout)
        except BaseException:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=15,
                    env=env,
                )
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.communicate(timeout=15)
            raise
        return process.returncode, output


def invoke(
    project: dict[str, object],
    command: dict[str, object],
    workspace: Path,
    python: str | None,
    *,
    execute: bool,
    env: dict[str, str],
) -> CheckReceipt:
    name, cid = str(project["id"]), str(command["id"])
    repo = confined(workspace, str(project["repo"]))
    if not execute:
        return CheckReceipt(
            name, cid, "skip", "not_run", "Plan only; command has not executed"
        )
    started = time.monotonic()
    if "builtin" in command:
        passed, reason = builtin_check(repo, command)
        return CheckReceipt(
            name,
            cid,
            "pass" if passed else "fail",
            "source_check",
            reason,
            duration_seconds=round(time.monotonic() - started, 3),
        )
    argv = strings(command["argv"], "argv")
    if any("{python}" in item for item in argv) and python is None:
        return CheckReceipt(
            name,
            cid,
            "fail",
            "missing_tool",
            "Project interpreter unavailable; configure --python PROJECT=PATH",
        )
    resolved = [a.replace("{python}", python or "") for a in argv]
    tool = shutil.which(resolved[0], path=env.get("PATH"))
    if tool is None:
        return CheckReceipt(
            name,
            cid,
            "fail",
            "missing_tool",
            f"Required executable unavailable: {argv[0]}",
        )
    for relative in strings(
        command.get("runtime_paths", []), "runtime_paths", empty=True
    ):
        if not confined(repo, relative).exists():
            return CheckReceipt(
                name,
                cid,
                "fail",
                "missing_tool",
                f"Installed dependency unavailable: {relative}",
            )
    if argv[0] == "gradle" and (
        not env.get("JAVA_HOME")
        or not (env.get("ANDROID_HOME") or env.get("ANDROID_SDK_ROOT"))
    ):
        return CheckReceipt(
            name,
            cid,
            "fail",
            "missing_tool",
            "Android build requires configured JAVA_HOME and ANDROID_HOME or ANDROID_SDK_ROOT",
        )
    for module in strings(command["python_modules"], "modules", empty=True):
        try:
            probe = subprocess.run(
                [
                    python or sys.executable,
                    "-c",
                    "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)",
                    module,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return CheckReceipt(
                name,
                cid,
                "fail",
                "missing_tool",
                "Configured Python tool probe unavailable",
            )
        if probe.returncode:
            return CheckReceipt(
                name,
                cid,
                "fail",
                "missing_tool",
                f"Required Python module unavailable: {module}",
            )
    resolved[0] = tool
    if python:
        env = {
            **env,
            "PATH": str(Path(python).parent) + os.pathsep + env.get("PATH", ""),
        }
    cwd = (
        workspace
        if command["cwd"] == "@workspace"
        else confined(repo, str(command["cwd"]))
    )
    try:
        returncode, output = bounded_process(
            resolved,
            cwd=cwd,
            env={**env, **({"PYTHON_BIN": python} if python else {})},
            timeout=int(str(command["timeout_seconds"])),
        )
        return CheckReceipt(
            name,
            cid,
            "pass" if returncode == 0 else "fail",
            "completed" if returncode == 0 else "check_failed",
            "Offline command completed; raw output intentionally omitted",
            returncode,
            round(time.monotonic() - started, 3),
            hashlib.sha256(output).hexdigest(),
        )
    except subprocess.TimeoutExpired:
        return CheckReceipt(
            name,
            cid,
            "fail",
            "timeout",
            "Configured bounded check timed out",
            duration_seconds=round(time.monotonic() - started, 3),
        )
    except OSError:
        return CheckReceipt(
            name,
            cid,
            "fail",
            "execution_error",
            "Executable or working directory unavailable",
        )


def run(
    manifest: dict[str, object],
    workspace: Path,
    *,
    mode: str,
    execute: bool,
    overrides: dict[str, str],
    selected: set[str],
    clean_home: bool,
    root: Path = ROOT,
) -> WorkspaceReceipt:
    receipt = WorkspaceReceipt(
        manifest_sha256=hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest(),
        mode=mode,
        executed=execute,
        clean_home=clean_home,
    )
    receipt.scope = "selected_projects" if selected else "workspace"
    receipt.inventory_errors = validate(manifest, workspace, root=root)
    if receipt.inventory_errors:
        return receipt
    projects = records(manifest["projects"], "projects")
    if selected - {str(p["id"]) for p in projects}:
        receipt.inventory_errors.append("Unknown selected project")
        return receipt
    # No API credentials or provider-native configuration flow into offline checks.
    permitted = {
        "PATH",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "TEMP",
        "TMP",
        "LANG",
        "LC_ALL",
        "JAVA_HOME",
        "ANDROID_HOME",
        "ANDROID_SDK_ROOT",
        "GRADLE_USER_HOME",
    }
    env = {key: value for key, value in os.environ.items() if key in permitted}
    if not clean_home:
        env.update(
            {
                key: os.environ[key]
                for key in ["HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA"]
                if key in os.environ
            }
        )
    env.update(
        PYTHONUTF8="1",
        PYTHONDONTWRITEBYTECODE="1",
        CI="true",
        npm_config_offline="true",
    )
    with tempfile.TemporaryDirectory(prefix="reconstruction-home-") as home:
        if clean_home:
            env.update(
                {
                    key: home
                    for key in [
                        "HOME",
                        "USERPROFILE",
                        "APPDATA",
                        "LOCALAPPDATA",
                        "XDG_CONFIG_HOME",
                        "XDG_CACHE_HOME",
                        "XDG_DATA_HOME",
                        "CODEX_HOME",
                        "CLAUDE_CONFIG_DIR",
                        "GEMINI_CLI_HOME",
                    ]
                }
            )
            env["GIT_CONFIG_GLOBAL"] = str(Path(home) / "empty.gitconfig")
            env["GIT_CONFIG_NOSYSTEM"] = "1"
        for project in projects:
            name = str(project["id"])
            if selected and name not in selected:
                receipt.checks.append(
                    CheckReceipt(
                        name,
                        "project",
                        "skip",
                        "not_selected",
                        "Explicit bounded selection; workspace-wide success not claimed",
                    )
                )
                continue
            repo = confined(workspace, str(project["repo"]))
            if shutil.which("git"):
                receipt.local_only_sources.extend(
                    source_readiness(project, repo, env=env)
                )
            else:
                receipt.checks.append(
                    CheckReceipt(
                        name,
                        "version-ownership",
                        "fail",
                        "missing_tool",
                        "Git is required to verify declared source version ownership",
                    )
                )
            python = resolve_python(repo, overrides.get(name))
            applicable = [
                command
                for command in records(project["commands"], "commands")
                if mode in strings(command["modes"], "modes")
            ]
            if not applicable:
                receipt.checks.append(
                    CheckReceipt(
                        name,
                        mode,
                        "skip",
                        "not_applicable",
                        "Documentation-only project has no compile/build stage; local links belong to fast/full checks",
                    )
                )
            for command in applicable:
                receipt.checks.append(
                    invoke(
                        project, command, workspace, python, execute=execute, env=env
                    )
                )
    receipt.status = (
        "pass"
        if execute
        and all(
            c.status == "pass" or c.category in {"not_selected", "not_applicable"}
            for c in receipt.checks
        )
        else "fail"
    )
    receipt.declared_contract_ready = (
        receipt.status == "pass" and not selected and not receipt.local_only_sources
    )
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["validate", "plan", "run"])
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(os.environ.get("BHANU_DEVELOPER_ROOT", ROOT.parent)),
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="CI contract check without sibling checkouts; not workspace readiness",
    )
    parser.add_argument("--mode", choices=sorted(MODES), default="fast")
    parser.add_argument("--project", action="append", default=[])
    parser.add_argument("--python", action="append", default=[], metavar="PROJECT=PATH")
    parser.add_argument("--clean-home", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = mapping(
            json.loads(args.manifest.read_text(encoding="utf-8")), "manifest"
        )
        if args.action == "validate":
            errors = validate(manifest, args.workspace_root, paths=not args.schema_only)
            print(
                json.dumps(
                    {
                        "schema_version": 1,
                        "scope": "schema_only"
                        if args.schema_only
                        else "workspace_inventory",
                        "status": "fail" if errors else "pass",
                        "errors": errors,
                    },
                    indent=2,
                )
            )
            return 1 if errors else 0
        if args.schema_only:
            parser.error("--schema-only is valid only for validate")
        overrides = {}
        for item in args.python:
            name, sep, path = item.partition("=")
            if not sep or not name or not path:
                parser.error("--python requires PROJECT=PATH")
            overrides[name] = path
        receipt = run(
            manifest,
            args.workspace_root,
            mode=args.mode,
            execute=args.action == "run",
            overrides=overrides,
            selected=set(args.project),
            clean_home=args.clean_home,
        )
        print(json.dumps(asdict(receipt), indent=2))
        return (
            0
            if receipt.status == "pass"
            or (args.action == "plan" and not receipt.inventory_errors)
            else 1
        )
    except (ValueError, OSError):
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "fail",
                    "errors": [
                        "Manifest could not be loaded; no file contents emitted"
                    ],
                }
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
