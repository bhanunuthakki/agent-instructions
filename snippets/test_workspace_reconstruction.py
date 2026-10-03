from __future__ import annotations

import copy
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

import pytest
from workspace_reconstruction import (
    MANIFEST,
    WorkspaceReceipt,
    builtin_check,
    invoke,
    mapping,
    records,
    run,
    validate,
)


def fixture_workspace(tmp_path: Path) -> tuple[dict[str, object], Path, Path]:
    workspace = tmp_path / "workspace"
    root = workspace / "agent-instructions"
    (root / "config").mkdir(parents=True)
    (root / "config" / "llm_usage_index.json").write_text('{"projects": []}')
    (root / "AGENTS_GUIDE.md").write_text(
        "<!-- BEGIN:projects -->\n| example | AGENTS.md |\n<!-- END:projects -->"
    )
    repo = workspace / "example"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "AGENTS.md").write_text("Offline fixture contract")
    (repo / "check.py").write_text('print("fixture")')
    project = {
        "id": "example",
        "repo": "example",
        "documentation": ["AGENTS.md"],
        "toolchain": ["Python >=3.11"],
        "install": ["No install"],
        "install_sources": ["AGENTS.md"],
        "canonical_generated": [
            {
                "canonical": ["AGENTS.md"],
                "generated": ["CLAUDE.md"],
                "regenerate": "fixture",
            }
        ],
        "llm": {
            "status": "not_applicable",
            "usage_index": "config/llm_usage_index.json",
            "entrypoints": [],
            "purpose_authority": "none",
            "prompt_schema_versions": "none",
            "adapters": [],
            "ledger_authority": "none",
            "eval_authority": "none",
            "residual_inventory": [],
        },
        "scheduled_jobs": ["none"],
        "state_boundaries": ["temporary fixture only"],
        "secret_boundaries": ["forbidden.env"],
        "vendor_harness_coupling": ["none"],
        "transition_recovery": "restore fixture",
        "hook_ci_disposition": "same offline command",
        "commands": [
            {
                "id": "check",
                "argv": ["{python}", "check.py"],
                "modes": ["fast", "full", "build"],
                "cwd": ".",
                "python_modules": [],
                "source_paths": ["check.py"],
                "offline_safe": True,
                "timeout_seconds": 30,
            }
        ],
    }
    manifest = {
        "schema_version": 1,
        "canonical_source": "config/workspace_reconstruction.json",
        "assessment_url": "https://linear.app/example/document/assessment-real",
        "population_authority": "AGENTS_GUIDE.md",
        "population_note": "fixture census",
        "regeneration": "hand maintained",
        "projects": [project],
    }
    return manifest, workspace, root


def test_inventory_rejects_omissions_duplicates_stale_paths_and_incomplete_fields(
    tmp_path: Path,
) -> None:
    manifest, workspace, root = fixture_workspace(tmp_path)
    assert validate(manifest, workspace, root=root) == []
    for mutate in [
        lambda x: x.update(projects=[]),
        lambda x: x["projects"].append(copy.deepcopy(x["projects"][0])),
        lambda x: x["projects"][0]["documentation"].append("missing.md"),
        lambda x: x["projects"][0].pop("state_boundaries"),
        lambda x: x["projects"][0].update(repo="../escape"),
    ]:
        invalid = copy.deepcopy(manifest)
        mutate(invalid)
        assert validate(invalid, workspace, root=root)


def test_secret_contents_are_never_read_by_inventory_or_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, workspace, root = fixture_workspace(tmp_path)
    secret = workspace / "example" / "forbidden.env"
    secret.write_text("SENTINEL_PRIVATE_VALUE")
    original = Path.read_text

    def guarded(
        path: Path, encoding: str | None = None, errors: str | None = None
    ) -> str:
        assert path != secret
        return original(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", guarded)
    assert not validate(manifest, workspace, root=root)
    receipt = run(
        manifest,
        workspace,
        mode="fast",
        execute=False,
        overrides={},
        selected=set(),
        clean_home=True,
        root=root,
    )
    assert "SENTINEL_PRIVATE_VALUE" not in json.dumps(asdict(receipt))
    assert receipt.checks[0].category == "not_run"
    assert receipt.status == "fail"


def test_missing_interpreter_and_module_are_failures_not_skips(tmp_path: Path) -> None:
    manifest, workspace, _ = fixture_workspace(tmp_path)
    project = records(manifest["projects"], "projects")[0]
    command = records(project["commands"], "commands")[0]
    result = invoke(
        project, command, workspace, None, execute=True, env=dict(os.environ)
    )
    assert result.status == "fail" and result.category == "missing_tool"
    command["python_modules"] = ["definitely_missing_reconstruction_tool"]
    result = invoke(
        project, command, workspace, sys.executable, execute=True, env=dict(os.environ)
    )
    assert result.status == "fail" and result.category == "missing_tool"


def test_real_success_failure_and_output_redaction(tmp_path: Path) -> None:
    manifest, workspace, _ = fixture_workspace(tmp_path)
    project = records(manifest["projects"], "projects")[0]
    command = records(project["commands"], "commands")[0]
    script = workspace / "example" / "check.py"
    script.write_text('print("SENTINEL_PRIVATE_VALUE")')
    result = invoke(
        project, command, workspace, sys.executable, execute=True, env=dict(os.environ)
    )
    assert result.status == "pass" and result.exit_code == 0 and result.output_sha256
    assert "SENTINEL_PRIVATE_VALUE" not in json.dumps(asdict(result))
    script.write_text("raise SystemExit(9)")
    result = invoke(
        project, command, workspace, sys.executable, execute=True, env=dict(os.environ)
    )
    assert result.status == "fail" and result.exit_code == 9


def test_clean_home_excludes_harness_autoload_and_api_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, workspace, root = fixture_workspace(tmp_path)
    script = workspace / "example" / "check.py"
    script.write_text(
        'import os,pathlib\nassert not os.environ.get("OPENAI_API_KEY")\nassert pathlib.Path(os.environ["HOME"]).name.startswith("reconstruction-home-")\nassert not (pathlib.Path(os.environ["HOME"])/".codex").exists()\n'
    )
    monkeypatch.setenv("OPENAI_API_KEY", "SENTINEL_PRIVATE_VALUE")
    receipt = run(
        manifest,
        workspace,
        mode="fast",
        execute=True,
        overrides={"example": sys.executable},
        selected=set(),
        clean_home=True,
        root=root,
    )
    assert receipt.status == "pass"
    assert receipt.clean_home and receipt.checks[0].status == "pass"


def test_source_compile_does_not_import_or_execute(tmp_path: Path) -> None:
    source = tmp_path / "unsafe.py"
    source.write_text('raise RuntimeError("must never execute")\n')
    okay, _ = builtin_check(
        tmp_path, {"builtin": "python_syntax", "paths": ["unsafe.py"]}
    )
    assert okay and not (tmp_path / "__pycache__").exists()
    source.write_text("broken syntax !")
    okay, _ = builtin_check(
        tmp_path, {"builtin": "python_syntax", "paths": ["unsafe.py"]}
    )
    assert not okay


def test_canonical_manifest_has_real_projects_and_nested_stacks() -> None:
    manifest = mapping(json.loads(MANIFEST.read_text()), "manifest")
    projects = records(manifest["projects"], "projects")
    assert len(projects) == 13
    assert len({p["id"] for p in projects}) == 13
    reading = next(p for p in projects if p["id"] == "reading-companion-app")
    assert {"core", "clients/android-xr", "clients/meta-rbd/dat-android"} <= {
        c.get("cwd") for c in records(reading["commands"], "commands")
    }
    assert mapping(reading["llm"], "llm")["status"] == "migration_required"
    maintenance = next(p for p in projects if p["id"] == "repo-maintenance")
    assert not any(
        "DryRun" in str(c.get("argv"))
        for c in records(maintenance["commands"], "commands")
    )


def test_subset_cannot_claim_whole_workspace_and_missing_nested_tool_is_explicit(
    tmp_path: Path,
) -> None:
    manifest, workspace, root = fixture_workspace(tmp_path)
    receipt = run(
        manifest,
        workspace,
        mode="fast",
        execute=True,
        overrides={"example": sys.executable},
        selected={"example"},
        clean_home=True,
        root=root,
    )
    assert receipt.status == "pass" and receipt.scope == "selected_projects"
    assert not receipt.declared_contract_ready
    project = records(manifest["projects"], "projects")[0]
    command = records(project["commands"], "commands")[0]
    command["runtime_paths"] = ["node_modules/typescript/bin/tsc"]
    missing = invoke(
        project, command, workspace, sys.executable, execute=True, env=dict(os.environ)
    )
    assert missing.status == "fail" and missing.category == "missing_tool"


def test_timeout_terminates_owned_command(tmp_path: Path) -> None:
    manifest, workspace, _ = fixture_workspace(tmp_path)
    (workspace / "example" / "check.py").write_text("import time\ntime.sleep(60)\n")
    project = records(manifest["projects"], "projects")[0]
    command = records(project["commands"], "commands")[0]
    command["timeout_seconds"] = 1
    result = invoke(
        project, command, workspace, sys.executable, execute=True, env=dict(os.environ)
    )
    assert result.status == "fail" and result.category == "timeout"
    assert result.duration_seconds < 10


@pytest.mark.parametrize("source", ["missing.py", "."])
def test_missing_builtin_source_cannot_pass(tmp_path: Path, source: str) -> None:
    okay, _ = builtin_check(tmp_path, {"builtin": "python_syntax", "paths": [source]})
    assert not okay


def test_declared_contract_readiness_covers_only_declared_sources(
    tmp_path: Path,
) -> None:
    import subprocess

    manifest, workspace, root = fixture_workspace(tmp_path)
    repo = workspace / "example"
    (repo / ".git").rmdir()
    for args in [
        ["git", "init", "-q"],
        ["git", "add", "AGENTS.md", "check.py"],
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-qm",
            "fixture",
        ],
    ]:
        subprocess.run(args, cwd=repo, check=True, capture_output=True)

    def receipt() -> WorkspaceReceipt:
        return run(
            manifest,
            workspace,
            mode="fast",
            execute=True,
            overrides={"example": sys.executable},
            selected=set(),
            clean_home=True,
            root=root,
        )

    before = copy.deepcopy(manifest)
    assert receipt().declared_contract_ready
    assert manifest == before
    (repo / "check.py").write_text('print("changed but passing")')
    changed = receipt()
    assert changed.status == "pass"
    assert not changed.declared_contract_ready
    assert changed.local_only_sources == ["example:check.py"]
    subprocess.run(["git", "restore", "check.py"], cwd=repo, check=True)
    project = records(manifest["projects"], "projects")[0]
    records(project["commands"], "commands")[0]["source_paths"] = ["."]
    (repo / "new_dependency.py").write_text("VALUE = 1")
    untracked = receipt()
    assert untracked.status == "pass" and not untracked.declared_contract_ready
    assert untracked.local_only_sources == ["example:."]


def test_source_checks_inspect_checkouts_under_artifact_directories(
    tmp_path: Path,
) -> None:
    repo = tmp_path / ".tmp" / "checkout"
    repo.mkdir(parents=True)
    (repo / "broken.py").write_text("broken syntax !")
    okay, _ = builtin_check(repo, {"builtin": "python_syntax", "paths": ["."]})
    assert not okay

    (repo / "broken.py").write_text("VALUE = 1")
    ignored = repo / ".tmp"
    ignored.mkdir()
    (ignored / "broken.py").write_text("broken syntax !")
    okay, reason = builtin_check(repo, {"builtin": "python_syntax", "paths": ["."]})
    assert okay and "1 source file(s) checked" in reason


def test_builtin_scan_rejects_escaping_file_symlink_before_reading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    private = tmp_path / "private.py"
    private.write_text("PRIVATE = 1")
    (repo / "linked.py").symlink_to(private)
    read = Path.read_text

    def guarded(path: Path, *args: object, **kwargs: object) -> str:
        assert path.resolve() != private, "outside source must never be read"
        return read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded)
    okay, _ = builtin_check(repo, {"builtin": "python_syntax", "paths": ["."]})
    assert not okay


def test_git_source_probes_use_isolated_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    from workspace_reconstruction import source_readiness

    manifest, workspace, _ = fixture_workspace(tmp_path)
    isolated = {"HOME": str(tmp_path / "isolated"), "PATH": os.environ["PATH"]}
    calls: list[object] = []

    def probe(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        assert kwargs.get("env") == isolated
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout=b"")

    monkeypatch.setattr(subprocess, "run", probe)
    assert (
        source_readiness(manifest["projects"][0], workspace / "example", env=isolated)
        == []
    )
    assert len(calls) == 3


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group lifecycle regression")
@pytest.mark.parametrize("interrupted", [False, True])
def test_abnormal_exit_terminates_owned_descendant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, interrupted: bool
) -> None:
    import subprocess
    import time

    from workspace_reconstruction import bounded_process

    pidfile = tmp_path / "child.pid"
    program = (
        "import subprocess,sys,time; from pathlib import Path; "
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
        f"Path({str(pidfile)!r}).write_text(str(child.pid)); time.sleep({0.1 if interrupted else 60})"
    )
    communicate = subprocess.Popen.communicate
    first = True

    def interrupt(process: subprocess.Popen[bytes], *args: object, **kwargs: object):
        nonlocal first
        if first:
            first = False
            deadline = time.monotonic() + 5
            while not pidfile.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert pidfile.exists()
            raise KeyboardInterrupt()
        return communicate(process, *args, **kwargs)

    if interrupted:
        monkeypatch.setattr(subprocess.Popen, "communicate", interrupt)
    error = KeyboardInterrupt if interrupted else subprocess.TimeoutExpired
    with pytest.raises(error):
        bounded_process(
            [sys.executable, "-c", program],
            cwd=tmp_path,
            env=dict(os.environ),
            timeout=1,
        )
    child_pid = pidfile.read_text()
    status = subprocess.run(
        ["ps", "-o", "stat=", "-p", child_pid],
        capture_output=True,
        text=True,
        check=False,
    )
    assert not status.stdout.strip() or status.stdout.strip().startswith("Z")
