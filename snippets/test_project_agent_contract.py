from __future__ import annotations

from pathlib import Path

import project_agent_contract as contract
import pytest


def write_visual_project(
    repo: Path, *, contract_target: str = "docs/UI_CONTRACT.md"
) -> None:
    (repo / "docs").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "AGENTS.md").write_text(
        "# Rules\n\n"
        "## Interface\n"
        "- Profile: dense-desktop\n"
        f"- Contract: {contract_target}\n"
        "- Executable authority: src/tokens.css\n"
        "- Render: npm run dev at 1440 x 900\n"
        "- Gate: npm test -- ui-contract\n",
        encoding="utf-8",
    )
    (repo / "docs" / "UI_CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
    (repo / "src" / "tokens.css").write_text(":root {}\n", encoding="utf-8")


def test_valid_visual_project_resolves_local_authorities(tmp_path: Path) -> None:
    write_visual_project(tmp_path)

    result = contract.check_repo(tmp_path)

    assert result.ok
    assert result.findings == ()


def test_missing_interface_block_is_reported(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")

    result = contract.check_repo(tmp_path)

    assert result.findings == ("missing ## Interface authority block",)


def test_foreign_contract_path_is_rejected(tmp_path: Path) -> None:
    write_visual_project(tmp_path, contract_target="../other/UI_CONTRACT.md")

    result = contract.check_repo(tmp_path)

    assert any("escapes the repository" in finding for finding in result.findings)


def test_missing_executable_authority_is_reported(tmp_path: Path) -> None:
    write_visual_project(tmp_path)
    (tmp_path / "src" / "tokens.css").unlink()

    result = contract.check_repo(tmp_path)

    assert any(
        "Executable authority does not exist" in finding for finding in result.findings
    )


def test_none_profile_requires_explicit_none_fields(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(contract.render_block("none"), encoding="utf-8")

    assert contract.check_repo(tmp_path).ok


def test_initializer_seeds_but_does_not_overwrite_local_authority(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")

    contract.initialize(tmp_path, "editorial-reading")

    assert "Profile: editorial-reading" in (tmp_path / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    assert "continuing authority" in (tmp_path / "docs" / "UI_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    with pytest.raises(ValueError, match="already exists"):
        contract.initialize(tmp_path, "touch-first")


def test_initializer_preflights_existing_contract_before_editing_rulebook(
    tmp_path: Path,
) -> None:
    rulebook = tmp_path / "AGENTS.md"
    rulebook.write_text("# Rules\n", encoding="utf-8")
    existing = tmp_path / "docs" / "UI_CONTRACT.md"
    existing.parent.mkdir()
    existing.write_text("# Existing authority\n", encoding="utf-8")

    with pytest.raises(ValueError, match="already exists"):
        contract.initialize(tmp_path, "dense-desktop")

    assert rulebook.read_text(encoding="utf-8") == "# Rules\n"
    assert existing.read_text(encoding="utf-8") == "# Existing authority\n"


def test_estate_discovery_uses_git_repositories_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (tmp_path / "Utility.app").mkdir()

    assert contract.project_dirs(tmp_path) == [repo]
