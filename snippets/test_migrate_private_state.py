from pathlib import Path

import pytest

from snippets.migrate_private_state import migrate


def test_migration_copies_live_governance_state_without_deleting_source(
    tmp_path: Path,
) -> None:
    source = tmp_path / "instructions"
    state = tmp_path / "private-state"
    files = {
        "governance/judge_ledger.jsonl": '{"fixture":"synthetic-ledger"}\n',
        "governance/judge_issuance.jsonl": '{"fixture":"synthetic-issuance"}\n',
        "governance/harden_capability_receipts/synthetic.json": (
            '{"fixture":"synthetic-receipt"}\n'
        ),
        "governance/harden_capability_evidence/synthetic/score.json": (
            '{"fixture":"synthetic-score"}\n'
        ),
        "config/harden_capability_registry.json": (
            '{"qualifications":[{"receipt_id":"synthetic"}]}\n'
        ),
        "config/harden_eval_policy.json": (
            '{"ratified":true,"ratifier":"Synthetic Owner"}\n'
        ),
    }
    for relative, content in files.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    result = migrate(source, state)

    assert result.copied == len(files)
    assert result.unchanged == 0
    for relative, content in files.items():
        assert (source / relative).read_text(encoding="utf-8") == content
        assert (state / relative).read_text(encoding="utf-8") == content

    repeated = migrate(source, state)
    assert repeated.copied == 0
    assert repeated.unchanged == len(files)


def test_migration_refuses_to_overwrite_different_private_state(tmp_path: Path) -> None:
    source = tmp_path / "instructions"
    state = tmp_path / "private-state"
    relative = Path("governance/judge_ledger.jsonl")
    (source / relative).parent.mkdir(parents=True)
    (state / relative).parent.mkdir(parents=True)
    (source / relative).write_text("source\n", encoding="utf-8")
    (state / relative).write_text("different\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="refusing to overwrite"):
        migrate(source, state)
