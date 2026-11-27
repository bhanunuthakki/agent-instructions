"""Validate config/common_modules.json schema and canonical owner references."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "config" / "common_modules.json"


def test_common_modules_map_schema_and_uniqueness() -> None:
    raw = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    assert raw["$schema"] == "internal://common-modules-map/v1"
    assert raw["schema_version"] == 1
    modules = raw["modules"]
    assert isinstance(modules, list) and modules

    capabilities: list[str] = []
    required = {"capability", "owner_repo", "canonical_paths", "governed_by", "summary"}
    for entry in modules:
        assert set(entry) == required
        assert isinstance(entry["capability"], str) and entry["capability"]
        assert isinstance(entry["owner_repo"], str) and entry["owner_repo"]
        assert isinstance(entry["canonical_paths"], list) and entry["canonical_paths"]
        assert isinstance(entry["governed_by"], list)
        assert isinstance(entry["summary"], str) and entry["summary"]
        capabilities.append(entry["capability"])
    assert len(capabilities) == len(set(capabilities))


def test_common_modules_map_targets_exist_when_repos_present() -> None:
    raw = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    workspace_root = ROOT.parent
    for entry in raw["modules"]:
        repo_dir = workspace_root / entry["owner_repo"]
        if not repo_dir.is_dir():
            continue
        for rel_path in entry["canonical_paths"]:
            assert (repo_dir / rel_path).exists(), f"missing {entry['owner_repo']}/{rel_path}"
        for ref in entry["governed_by"]:
            repo_name, _, rel = ref.partition("/")
            ref_repo = workspace_root / repo_name
            if ref_repo.is_dir():
                assert (ref_repo / rel).exists(), f"missing {ref}"
