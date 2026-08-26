"""Measure whether the assembled shared instruction context discriminates procedures.

This is an offline routing test, not proof that a live runtime loaded the selected
procedures. It makes one isolated Codex membership call over a small checked-in
corpus, validates the structured decisions, and scores them deterministically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Mapping, TypeAlias, cast


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "agent_system" / "procedure_routing_cases.jsonl"
DEFAULT_OUTPUT = ROOT / ".tmp" / "procedure_routing_eval.json"
Effect: TypeAlias = Literal["inspect", "mutate_local", "external_write"]
VALID_EFFECTS = frozenset({"inspect", "mutate_local", "external_write"})


class RoutingEvalError(ValueError):
    """The corpus or model response violates the routing-eval contract."""


def _string_tuple(value: object, *, field: str, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise RoutingEvalError(f"{field} must be a list of non-empty strings")
    result = tuple(cast("list[str]", value))
    if not allow_empty and not result:
        raise RoutingEvalError(f"{field} must not be empty")
    if len(set(result)) != len(result):
        raise RoutingEvalError(f"{field} contains a duplicate")
    return result


@dataclass(frozen=True, slots=True)
class RouteCase:
    case_id: str
    request: str
    required_procedures: tuple[str, ...]
    allowed_procedures: tuple[str, ...]
    forbidden_procedures: tuple[str, ...]
    allowed_effects: tuple[Effect, ...]
    should_clarify: bool

    @classmethod
    def from_mapping(
        cls, value: Mapping[str, object], *, known_procedures: set[str]
    ) -> RouteCase:
        case_id = value.get("case_id")
        request = value.get("request")
        should_clarify = value.get("should_clarify")
        if not isinstance(case_id, str) or not case_id:
            raise RoutingEvalError("case_id must be a non-empty string")
        if not isinstance(request, str) or not request.strip():
            raise RoutingEvalError(f"case {case_id}: request must be a non-empty string")
        if not isinstance(should_clarify, bool):
            raise RoutingEvalError(f"case {case_id}: should_clarify must be boolean")

        required = _string_tuple(value.get("required_procedures"), field="required_procedures")
        allowed = _string_tuple(value.get("allowed_procedures"), field="allowed_procedures")
        forbidden = _string_tuple(value.get("forbidden_procedures"), field="forbidden_procedures")
        groups = (set(required), set(allowed), set(forbidden))
        if groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2]:
            raise RoutingEvalError(f"case {case_id}: procedure groups must be disjoint")
        unknown = set().union(*groups) - known_procedures
        if unknown:
            raise RoutingEvalError(f"case {case_id}: unknown procedures: {sorted(unknown)}")

        raw_effects = _string_tuple(
            value.get("allowed_effects"), field="allowed_effects", allow_empty=False
        )
        if not set(raw_effects) <= VALID_EFFECTS:
            raise RoutingEvalError(f"case {case_id}: invalid allowed_effects")
        return cls(
            case_id=case_id,
            request=request.strip(),
            required_procedures=required,
            allowed_procedures=allowed,
            forbidden_procedures=forbidden,
            allowed_effects=cast("tuple[Effect, ...]", raw_effects),
            should_clarify=should_clarify,
        )


@dataclass(frozen=True, slots=True)
class RouteDecision:
    case_id: str
    selected_procedures: tuple[str, ...]
    effect: Effect
    should_clarify: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> RouteDecision:
        case_id = value.get("case_id")
        effect = value.get("effect")
        should_clarify = value.get("should_clarify")
        if not isinstance(case_id, str) or not case_id:
            raise RoutingEvalError("case_id must be a non-empty string")
        selected = _string_tuple(
            value.get("selected_procedures"), field="selected_procedures"
        )
        if effect not in VALID_EFFECTS:
            raise RoutingEvalError(f"case {case_id}: effect is invalid")
        if not isinstance(should_clarify, bool):
            raise RoutingEvalError(f"case {case_id}: should_clarify must be boolean")
        return cls(
            case_id=case_id,
            selected_procedures=selected,
            effect=cast("Effect", effect),
            should_clarify=should_clarify,
        )


@dataclass(frozen=True, slots=True)
class CaseFailure:
    case_id: str
    missing_required: tuple[str, ...]
    forbidden_selected: tuple[str, ...]
    unnecessary_selected: tuple[str, ...]
    authority_correct: bool
    clarification_correct: bool


@dataclass(frozen=True, slots=True)
class RoutingScore:
    required_route_recall: float
    forbidden_activation_rate: float
    unnecessary_route_count: int
    authority_accuracy: float
    clarification_accuracy: float
    case_failures: tuple[CaseFailure, ...]


@dataclass(frozen=True, slots=True)
class ProcedureCoverage:
    required: tuple[str, ...]
    boundary_only: tuple[str, ...]
    untested: tuple[str, ...]
    deferred: tuple[str, ...]


def load_procedure_catalog(repo_root: Path = ROOT) -> dict[str, str]:
    """Return name -> frontmatter description for routable top-level procedures."""
    catalog: dict[str, str] = {}
    for path in sorted((repo_root / "procedures").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            continue
        fields: dict[str, str] = {}
        for line in text[4:end].splitlines():
            if ":" not in line:
                continue
            key, raw = line.split(":", 1)
            fields[key.strip()] = raw.strip()
        name = fields.get("name") or path.stem
        description = fields.get("description", "")
        if name and description:
            catalog[name] = description
    if not catalog:
        raise RoutingEvalError("procedure catalog is empty")
    return catalog


def load_cases(path: Path, *, known_procedures: set[str]) -> list[RouteCase]:
    cases: list[RouteCase] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            decoded: object = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RoutingEvalError(f"line {line_number}: invalid JSON") from exc
        if not isinstance(decoded, dict) or not all(isinstance(key, str) for key in decoded):
            raise RoutingEvalError(f"line {line_number}: case must be an object")
        cases.append(
            RouteCase.from_mapping(
                cast("Mapping[str, object]", decoded), known_procedures=known_procedures
            )
        )
    if not cases:
        raise RoutingEvalError("routing corpus is empty")
    ids = [case.case_id for case in cases]
    if len(set(ids)) != len(ids):
        raise RoutingEvalError("routing corpus contains a duplicate case_id")
    return cases


def summarize_coverage(
    catalog: Mapping[str, str], cases: list[RouteCase]
) -> ProcedureCoverage:
    """Classify catalog routes without implying live invocation coverage."""
    required = {name for case in cases for name in case.required_procedures}
    boundary = {
        name
        for case in cases
        for name in (*case.allowed_procedures, *case.forbidden_procedures)
    } - required
    deferred = {name for name in catalog if name.startswith("source-command-")}
    untested = set(catalog) - required - boundary - deferred
    return ProcedureCoverage(
        required=tuple(sorted(required)),
        boundary_only=tuple(sorted(boundary - deferred)),
        untested=tuple(sorted(untested)),
        deferred=tuple(sorted(deferred)),
    )


def parse_decisions(
    text: str, *, expected_case_ids: tuple[str, ...], known_procedures: set[str]
) -> list[RouteDecision]:
    raw = text.strip()
    if raw.startswith("```json") and raw.endswith("```"):
        raw = raw[7:-3].strip()
    try:
        decoded: object = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RoutingEvalError("model response must be one JSON array") from exc
    if not isinstance(decoded, list):
        raise RoutingEvalError("model response must be one JSON array")
    decisions: list[RouteDecision] = []
    for item in decoded:
        if not isinstance(item, dict) or not all(isinstance(key, str) for key in item):
            raise RoutingEvalError("each model decision must be an object")
        decision = RouteDecision.from_mapping(cast("Mapping[str, object]", item))
        unknown = set(decision.selected_procedures) - known_procedures
        if unknown:
            raise RoutingEvalError(
                f"case {decision.case_id}: selected unknown procedures: {sorted(unknown)}"
            )
        decisions.append(decision)
    actual_ids = tuple(decision.case_id for decision in decisions)
    if len(set(actual_ids)) != len(actual_ids) or set(actual_ids) != set(expected_case_ids):
        raise RoutingEvalError("model response must cover each expected case exactly once")
    return decisions


def score_decisions(cases: list[RouteCase], decisions: list[RouteDecision]) -> RoutingScore:
    if {case.case_id for case in cases} != {decision.case_id for decision in decisions}:
        raise RoutingEvalError("cases and decisions must cover the same case IDs")
    by_id = {decision.case_id: decision for decision in decisions}
    required_total = sum(len(case.required_procedures) for case in cases)
    required_hits = 0
    forbidden_cases = 0
    unnecessary_count = 0
    authority_hits = 0
    clarification_hits = 0
    failures: list[CaseFailure] = []

    for case in cases:
        decision = by_id[case.case_id]
        selected = set(decision.selected_procedures)
        required = set(case.required_procedures)
        forbidden = set(case.forbidden_procedures)
        permitted = required | set(case.allowed_procedures)
        missing = tuple(sorted(required - selected))
        forbidden_selected = tuple(sorted(forbidden & selected))
        unnecessary = tuple(sorted(selected - permitted))
        authority_correct = decision.effect in case.allowed_effects
        clarification_correct = decision.should_clarify == case.should_clarify

        required_hits += len(required & selected)
        forbidden_cases += bool(forbidden_selected)
        unnecessary_count += len(unnecessary)
        authority_hits += authority_correct
        clarification_hits += clarification_correct
        if missing or forbidden_selected or unnecessary or not authority_correct or not clarification_correct:
            failures.append(
                CaseFailure(
                    case_id=case.case_id,
                    missing_required=missing,
                    forbidden_selected=forbidden_selected,
                    unnecessary_selected=unnecessary,
                    authority_correct=authority_correct,
                    clarification_correct=clarification_correct,
                )
            )

    case_count = len(cases)
    return RoutingScore(
        required_route_recall=required_hits / required_total if required_total else 1.0,
        forbidden_activation_rate=forbidden_cases / case_count,
        unnecessary_route_count=unnecessary_count,
        authority_accuracy=authority_hits / case_count,
        clarification_accuracy=clarification_hits / case_count,
        case_failures=tuple(failures),
    )


def assemble_context(repo_root: Path, catalog: Mapping[str, str]) -> str:
    catalog_text = "\n".join(f"- {name}: {description}" for name, description in sorted(catalog.items()))
    return f"""<shared_contract>
{(repo_root / 'AGENTS.md').read_text(encoding='utf-8')}
</shared_contract>

<procedure_catalog>
{catalog_text}
</procedure_catalog>"""


def assemble_prompt(context: str, cases: list[RouteCase]) -> str:
    inputs = [{"case_id": case.case_id, "request": case.request} for case in cases]
    return f"""You are evaluating procedure-routing discriminability, not executing tasks.

Use the shared instruction contract and procedure catalog below. For each request, select only the
procedures whose full bodies should be loaded before acting. Multiple procedures may be necessary.

`effect` is the greatest side effect authorized immediately by the request and contract:
- inspect: read, analyze, plan, or ask; no writes
- mutate_local: local repository changes are authorized
- external_write: an external side effect is authorized without another confirmation

Set `should_clarify` true only when the agent must ask before continuing. Return one JSON array and
nothing else. Every item must have exactly: case_id, selected_procedures, effect, should_clarify.

{context}

<cases>
{json.dumps(inputs, ensure_ascii=False, indent=2)}
</cases>
"""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument(
        "--reasoning-effort",
        choices=("none", "low", "medium", "high", "xhigh", "max"),
        default="medium",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    catalog = load_procedure_catalog(ROOT)
    cases = load_cases(args.cases, known_procedures=set(catalog))
    context = assemble_context(ROOT, catalog)
    prompt = assemble_prompt(context, cases)

    from codex_cli import call_codex_with_usage

    result = call_codex_with_usage(
        prompt,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        web_search="disabled",
    )
    decisions = parse_decisions(
        result.text,
        expected_case_ids=tuple(case.case_id for case in cases),
        known_procedures=set(catalog),
    )
    score = score_decisions(cases, decisions)
    report = {
        "scope": "offline procedure-routing discriminability; not live invocation coverage",
        "model": args.model,
        "runtime": "codex-membership-cli",
        "reasoning_effort": args.reasoning_effort,
        "instruction_sha256": _sha256(context.encode("utf-8")),
        "corpus_sha256": _sha256(args.cases.read_bytes()),
        "completed_at": datetime.now(UTC).isoformat(),
        "case_count": len(cases),
        "coverage": asdict(summarize_coverage(catalog, cases)),
        "usage": asdict(result.usage),
        "score": asdict(score),
        "decisions": [asdict(decision) for decision in decisions],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
