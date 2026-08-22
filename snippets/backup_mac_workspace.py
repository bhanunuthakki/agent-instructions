#!/usr/bin/env python3
"""Create a static, Drive-safe backup of Mac workspace and recovery material.

This is deliberately not a database backup. Windows remains the only writer of
the live Earnings and Portfolio Tracker databases.  The archive excludes every
SQLite database and its WAL/SHM sidecars, credentials, and rebuildable files.
It includes Git metadata and uncommitted source work so it complements GitHub
without turning Google Drive into a live worktree synchronizer.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


ARCHIVE_PREFIX = "mac_workspace_"
ARCHIVE_SUFFIX = ".tar.gz"
DEFAULT_KEEP = 3
APPLICATION_REPOSITORIES = (
    ("Earnings-Summary", "earnings-summary"),
    ("Portfolio-Tracker", "portfolio-tracker"),
    ("Date-Suggester", "date-suggester"),
    ("Angel-Memos", "angel-memos"),
    ("Blog-Engine", "blog-engine"),
    ("Harness", "harness"),
    ("Huntdesk", "huntdesk"),
    ("MyClaw", "myclaw"),
    ("Reading-Companion-App", "reading-companion-app"),
    ("Repo-Maintenance", "repo-maintenance"),
    ("Wealthplan", "wealthplan"),
    ("XR-Glasses-Dev-Guide", "xr-glasses-dev-guide"),
    ("Resume-System", "bhanu-resume-system"),
)
EXCLUDED_DIRS = {
    ".agents",
    ".claude",
    ".codex",
    ".codex-membership",
    ".gemini",
    ".npm",
    ".tools",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tmp",
    "build",
    "dist",
    "output",
}
SECRET_FILE_RE = re.compile(
    r"(?:^|/)(?:\.env(?:\..*)?|[^/]*credentials[^/]*\.json|"
    r"[^/]*token[^/]*\.json|oauth_creds\.json|google_accounts\.json|"
    r"[^/]*client_secret[^/]*\.json|[^/]*service_account[^/]*\.json|"
    r"[^/]*secrets\.(?:json|ya?ml|toml|env)|[^/]*\.(?:pem|key|p12|pfx|jks|keystore|secret))$",
    re.IGNORECASE,
)
LIVE_DATABASE_RE = re.compile(r"(?:\.db(?:-(?:wal|shm))?|\.sqlite(?:-(?:wal|shm))?)$", re.IGNORECASE)


@dataclass(frozen=True)
class Source:
    label: str
    path: Path


def should_exclude(relative_path: Path) -> bool:
    """Return true for cloud-unsafe or regenerable content, never for .git."""
    parts = relative_path.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    if any(part in {".tmp.driveupload", "worktrees"} for part in parts):
        return True
    normalized = relative_path.as_posix()
    return bool(SECRET_FILE_RE.search(normalized) or LIVE_DATABASE_RE.search(normalized))


def discover_drive_root(cloud_storage: Path) -> Path:
    """Find the active Google Drive Stream root without embedding an account name."""
    candidates = sorted(cloud_storage.glob("GoogleDrive-*/My Drive"))
    existing = [candidate for candidate in candidates if candidate.is_dir()]
    if len(existing) != 1:
        raise RuntimeError(
            "expected exactly one Google Drive Stream root under "
            f"{cloud_storage}; found {len(existing)}"
        )
    return existing[0]


def iter_source_files(source: Source) -> Iterable[tuple[Path, Path]]:
    """Yield regular, eligible files as (absolute path, archive-relative path)."""
    for path in sorted(source.path.rglob("*")):
        try:
            if path.is_symlink() or not path.is_file():
                continue
        except OSError:
            continue
        relative = Path(source.label) / path.relative_to(source.path)
        if not should_exclude(relative):
            yield path, relative


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def human_bytes(value: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{value} B"
        value /= 1024
    raise AssertionError("unreachable")


def build_archive(sources: list[Source], archive: Path, *, dry_run: bool) -> dict[str, object]:
    included: list[dict[str, object]] = []
    excluded = 0
    for source in sources:
        for path in source.path.rglob("*"):
            try:
                if path.is_file() and not path.is_symlink() and should_exclude(
                    Path(source.label) / path.relative_to(source.path)
                ):
                    excluded += 1
            except OSError:
                continue
        for absolute, relative in iter_source_files(source):
            included.append(
                {
                    "path": relative.as_posix(),
                    "bytes": absolute.stat().st_size,
                    "sha256": sha256_file(absolute),
                }
            )
    manifest = {
        "format": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "sources": [{"label": source.label, "path": str(source.path)} for source in sources],
        "included_file_count": len(included),
        "excluded_file_count": excluded,
        "estimated_bytes": sum(item["bytes"] for item in included),
        "files": included,
    }
    if dry_run:
        return manifest

    restore = """Mac workspace/recovery backup restore procedure
================================================
1. Copy this archive from Google Drive to a local temporary directory.
2. Verify: python3 snippets/backup_mac_workspace.py --verify <archive>.
3. Extract into a NEW local directory, never directly into ~/Developer.
4. Review Git status in each restored repository, then copy only wanted files.

Included: Git history and uncommitted source/recovery files.
Excluded: live SQLite databases and sidecars, credentials/tokens/.env files,
virtual environments, node_modules, caches, build output, and temporary files.
Windows remains the sole writer and backup owner for live Earnings and Portfolio
Tracker databases; restore those only through the Windows-tested DB procedure.
"""
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as tar:
        for item in included:
            source_path = next(
                source.path / Path(item["path"]).relative_to(source.label)  # type: ignore[arg-type]
                for source in sources
                if str(item["path"]).startswith(source.label + "/")
            )
            tar.add(source_path, arcname=item["path"], recursive=False)
        for name, contents in {
            "MANIFEST.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            "RESTORE.md": restore,
        }.items():
            encoded = contents.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(encoded)
            info.mtime = int(datetime.now(UTC).timestamp())
            tar.addfile(info, fileobj=io.BytesIO(encoded))
    return manifest


def verify_archive(archive: Path) -> dict[str, object]:
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        names = {member.name for member in members}
        if {"MANIFEST.json", "RESTORE.md"} - names:
            raise RuntimeError("archive is missing MANIFEST.json or RESTORE.md")
        unsafe = [member.name for member in members if member.isfile() and should_exclude(Path(member.name))]
        if unsafe:
            raise RuntimeError(f"archive contains excluded content: {unsafe[:3]}")
        manifest_handle = tar.extractfile("MANIFEST.json")
        if manifest_handle is None:
            raise RuntimeError("cannot read MANIFEST.json")
        manifest = json.loads(manifest_handle.read().decode("utf-8"))
        for item in manifest["files"]:
            handle = tar.extractfile(item["path"])
            if handle is None:
                raise RuntimeError(f"archive missing manifest member: {item['path']}")
            digest = hashlib.sha256(handle.read()).hexdigest()
            if digest != item["sha256"]:
                raise RuntimeError(f"checksum mismatch: {item['path']}")
    return manifest


def prune_archives(destination: Path, keep: int) -> list[Path]:
    archives = sorted(destination.glob(f"{ARCHIVE_PREFIX}*{ARCHIVE_SUFFIX}"))
    stale = archives[:-keep] if len(archives) > keep else []
    for archive in stale:
        archive.unlink()
    return stale


def parser() -> argparse.ArgumentParser:
    home = Path.home()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="show source, exclusions, and destination only")
    p.add_argument("--verify", type=Path, help="verify an existing archive and exit")
    p.add_argument("--developer-root", type=Path, default=home / "Developer")
    p.add_argument(
        "--agent-instructions-root",
        type=Path,
        default=Path("/Applications/agent-instructions"),
    )
    p.add_argument("--applications-root", type=Path, default=Path("/Applications"))
    p.add_argument("--claude-projects-root", type=Path, default=home / "Documents" / "Claude" / "Projects")
    p.add_argument("--cloud-storage", type=Path, default=home / "Library" / "CloudStorage")
    p.add_argument("--log-dir", type=Path, default=home / "Library" / "Logs" / "MacWorkspaceBackup")
    p.add_argument("--keep", type=int, default=DEFAULT_KEEP)
    return p


def configured_sources(args: argparse.Namespace) -> list[Source]:
    return [
        Source("Developer", args.developer_root),
        Source("Agent-Instructions", args.agent_instructions_root),
        *[
            Source(label, args.applications_root / directory)
            for label, directory in APPLICATION_REPOSITORIES
        ],
        Source("Claude-Projects", args.claude_projects_root),
    ]


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.verify:
        manifest = verify_archive(args.verify)
        print(f"OK verified {args.verify}: {manifest['included_file_count']} files")
        return 0
    if args.keep < 1:
        raise ValueError("--keep must be at least 1")
    sources = configured_sources(args)
    present = [source for source in sources if source.path.is_dir()]
    missing = [source for source in sources if not source.path.is_dir()]
    if not present:
        raise RuntimeError("no configured backup sources exist")
    drive_root = discover_drive_root(args.cloud_storage)
    destination = drive_root / "scratch-backups"
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")
    local_archive = Path(tempfile.gettempdir()) / f"{ARCHIVE_PREFIX}{stamp}{ARCHIVE_SUFFIX}"
    manifest = build_archive(present, local_archive, dry_run=args.dry_run)
    print(f"destination: {destination}")
    print(f"schedule proposal: Saturday 01:30 America/Los_Angeles (inactive until approved)")
    print(f"retention: keep {args.keep} completed archives")
    print("sources: " + ", ".join(str(source.path) for source in present))
    if missing:
        print("not present (skipped): " + ", ".join(str(source.path) for source in missing))
    print(
        f"contents: {manifest['included_file_count']} files; "
        f"excluded: {manifest['excluded_file_count']} files; "
        f"estimated size: {human_bytes(manifest['estimated_bytes'])}"
    )
    print("exclusions: credentials/tokens/.env, SQLite databases/WAL/SHM, virtualenvs, node_modules, caches, build output, temporary files")
    log_record = {
        "created_at": datetime.now(UTC).isoformat(),
        "mode": "dry-run" if args.dry_run else "live",
        "destination": str(destination),
        "sources": [str(source.path) for source in present],
        "missing_sources": [str(source.path) for source in missing],
        "included_file_count": manifest["included_file_count"],
        "excluded_file_count": manifest["excluded_file_count"],
        "estimated_bytes": manifest["estimated_bytes"],
        "retention_keep": args.keep,
        "schedule": "Saturday 01:30 America/Los_Angeles; inactive pending owner approval",
    }
    args.log_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.log_dir / f"mac-workspace-backup-{stamp}-{'dryrun' if args.dry_run else 'live'}.json"
    log_path.write_text(json.dumps(log_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"log: {log_path}")
    if args.dry_run:
        for item in manifest["files"][:200]:
            print(f"  {item['path']}")
        if manifest["included_file_count"] > 200:
            print("  ... (remaining entries omitted; manifest would list every file)")
        return 0
    try:
        verified = verify_archive(local_archive)
        destination.mkdir(parents=True, exist_ok=True)
        final = destination / local_archive.name
        uploading = destination / (local_archive.name + ".uploading")
        shutil.copy2(local_archive, uploading)
        os.replace(uploading, final)
        pruned = prune_archives(destination, args.keep)
        print(f"published: {final}")
        print(f"verified: {verified['included_file_count']} files; pruned: {len(pruned)}")
    finally:
        local_archive.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
