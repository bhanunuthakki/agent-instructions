from pathlib import Path

import pytest

from snippets.private_state import PRIVATE_STATE_ENV, private_state_root


def test_private_state_defaults_to_ignored_repository_directory(tmp_path: Path) -> None:
    assert private_state_root(tmp_path, environ={}) == tmp_path / ".private-state"


def test_private_state_accepts_absolute_override(tmp_path: Path) -> None:
    configured = tmp_path / "outside" / "agent-state"
    assert (
        private_state_root(
            tmp_path,
            environ={PRIVATE_STATE_ENV: str(configured)},
        )
        == configured
    )


def test_private_state_rejects_relative_override(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must be an absolute path"):
        private_state_root(
            tmp_path,
            environ={PRIVATE_STATE_ENV: "relative/state"},
        )
