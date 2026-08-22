"""Regression checks for the Mac workspace/recovery archive contract."""

from __future__ import annotations

import plistlib
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import backup_mac_workspace as backup  # noqa: E402


def test_live_databases_and_credentials_are_excluded() -> None:
    assert backup.should_exclude(Path("Developer/project/data/portfolio.db"))
    assert backup.should_exclude(Path("Developer/project/data/portfolio.db-wal"))
    assert backup.should_exclude(Path("Developer/project/.env"))
    assert backup.should_exclude(Path("Developer/project/secrets/token.json"))
    assert backup.should_exclude(Path("Developer/project/.codex-membership/auth.json"))
    assert backup.should_exclude(Path("Developer/project/.claude/settings.json"))


def test_git_and_uncommitted_source_files_are_preserved() -> None:
    assert not backup.should_exclude(Path("Developer/project/.git/HEAD"))
    assert not backup.should_exclude(Path("Developer/project/src/unfinished.py"))


def test_drive_root_is_discovered_without_an_account_name(tmp_path: Path) -> None:
    drive_root = tmp_path / "GoogleDrive-account-id" / "My Drive"
    drive_root.mkdir(parents=True)

    assert backup.discover_drive_root(tmp_path) == drive_root


def test_default_sources_include_the_instruction_clone_outside_developer() -> None:
    sources = backup.configured_sources(backup.parser().parse_args([]))

    assert ("Agent-Instructions", Path("/Applications/agent-instructions")) in [
        (source.label, source.path) for source in sources
    ]


def test_default_sources_cover_expected_application_repositories_but_not_recovery() -> None:
    sources = backup.configured_sources(backup.parser().parse_args([]))
    labels_and_paths = {(source.label, source.path) for source in sources}

    assert ("Earnings-Summary", Path("/Applications/earnings-summary")) in labels_and_paths
    assert ("MyClaw", Path("/Applications/myclaw")) in labels_and_paths
    assert ("Resume-System", Path("/Applications/bhanu-resume-system")) in labels_and_paths
    assert (
        "XR-Glasses-Dev-Guide",
        Path("/Applications/xr-glasses-dev-guide"),
    ) in labels_and_paths
    assert all(source.label != "Migration-Recovery" for source in sources)


def test_launchd_schedule_is_saturday_at_0130() -> None:
    plist_path = (
        Path(__file__).parent.parent
        / "launchd"
        / "com.bhanu.mac-workspace-backup.plist.disabled"
    )
    with plist_path.open("rb") as handle:
        schedule = plistlib.load(handle)["StartCalendarInterval"]

    assert schedule == {"Weekday": 6, "Hour": 1, "Minute": 30}


def test_archive_verification_preserves_git_and_rejects_unsafe_files(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / ".git").mkdir(parents=True)
    (project / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (project / "src").mkdir()
    (project / "src" / "uncommitted.py").write_text("answer = 42\n", encoding="utf-8")
    (project / ".env").write_text("not-a-real-secret\n", encoding="utf-8")
    (project / "data.db").write_bytes(b"not a database")
    archive = tmp_path / "workspace.tar.gz"

    manifest = backup.build_archive([backup.Source("Developer", project)], archive, dry_run=False)
    verified = backup.verify_archive(archive)

    assert manifest["included_file_count"] == 2
    assert verified["included_file_count"] == 2
    assert manifest["estimated_bytes"] == len("ref: refs/heads/main\n") + len("answer = 42\n")


def test_sqlite_snapshot_is_consistent_and_archive_safe(tmp_path: Path) -> None:
    source = tmp_path / "live.db"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE notes (body TEXT NOT NULL)")
        connection.execute("INSERT INTO notes VALUES ('preserved')")
    snapshot = tmp_path / "Database-Snapshots" / "HuntDesk" / "huntdesk.db.snapshot"

    backup.snapshot_sqlite_database(source, snapshot)

    with sqlite3.connect(f"file:{snapshot.as_posix()}?mode=ro", uri=True) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("SELECT body FROM notes").fetchone() == ("preserved",)
    assert not backup.should_exclude(Path("Database-Snapshots/HuntDesk/huntdesk.db.snapshot"))


def test_dry_run_writes_a_structured_log(tmp_path: Path) -> None:
    developer = tmp_path / "Developer"
    developer.mkdir()
    (developer / "notes.txt").write_text("uncommitted work\n", encoding="utf-8")
    cloud = tmp_path / "CloudStorage"
    (cloud / "GoogleDrive-id" / "My Drive").mkdir(parents=True)
    logs = tmp_path / "logs"

    assert backup.main(
        [
            "--dry-run",
            "--developer-root",
            str(developer),
            "--claude-projects-root",
            str(tmp_path / "absent-claude"),
            "--cloud-storage",
            str(cloud),
            "--log-dir",
            str(logs),
        ]
    ) == 0
    receipt = next(logs.glob("*.json"))
    assert '"mode": "dry-run"' in receipt.read_text(encoding="utf-8")


def test_run_output_describes_the_configured_schedule(
    tmp_path: Path, capsys
) -> None:
    developer = tmp_path / "Developer"
    developer.mkdir()
    (developer / "notes.txt").write_text("work\n", encoding="utf-8")
    cloud = tmp_path / "CloudStorage"
    (cloud / "GoogleDrive-id" / "My Drive").mkdir(parents=True)

    assert backup.main(
        [
            "--dry-run",
            "--developer-root",
            str(developer),
            "--claude-projects-root",
            str(tmp_path / "absent-claude"),
            "--cloud-storage",
            str(cloud),
            "--log-dir",
            str(tmp_path / "logs"),
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "configured schedule: Saturday 01:30 America/Los_Angeles" in output
    assert "inactive until approved" not in output
