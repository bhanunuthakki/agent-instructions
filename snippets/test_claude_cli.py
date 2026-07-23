from __future__ import annotations

import claude_cli


def test_default_membership_model_is_current_workhorse() -> None:
    assert claude_cli.DEFAULT_MODEL == "claude-sonnet-5"
