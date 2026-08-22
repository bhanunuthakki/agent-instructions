#!/bin/sh
# Install the tracked shared agent rules from a Mac clone, then wire every
# Git repository beside this clone to the same safety hooks.
set -eu

ROOT_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PROJECT_ROOT=${BHANU_DEVELOPER_ROOT:-"$(dirname "$ROOT_REPO")"}
PYTHON_BIN=${PYTHON_BIN:-python3}

if [ "$(uname -s)" != "Darwin" ]; then
    printf '%s\n' "warning: bootstrap_mac.sh is intended for macOS" >&2
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    printf '%s\n' "Python 3 is required before running this bootstrap." >&2
    exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
    printf '%s\n' "Node/npm is required before running this bootstrap." >&2
    exit 1
fi

mkdir -p "$PROJECT_ROOT"
npm install --prefix "$ROOT_REPO/.tools" @openai/codex

AGENT_INSTRUCTIONS_HOME="$ROOT_REPO"
export AGENT_INSTRUCTIONS_HOME

"$PYTHON_BIN" "$ROOT_REPO/snippets/sync_agent_stubs.py" --artifacts-only

# Project CLAUDE.md/GEMINI.md wrappers are tracked in each repository. Only
# wire Git repositories here; do not regenerate the tracked human guide from a
# machine-specific subset of the project root.
for PROJECT_DIR in "$PROJECT_ROOT"/*; do
    [ -d "$PROJECT_DIR/.git" ] || continue
    [ "$(CDPATH= cd -- "$PROJECT_DIR" && pwd)" = "$ROOT_REPO" ] && continue
    git -C "$PROJECT_DIR" config core.hooksPath "$ROOT_REPO/githooks"
done

git -C "$ROOT_REPO" config core.hooksPath "$ROOT_REPO/githooks"
"$PYTHON_BIN" "$ROOT_REPO/snippets/sync_agent_stubs.py" --check --artifacts-only

printf '%s\n' \
    "Shared agent setup complete." \
    "Codex global rules: $HOME/.codex/AGENTS.md" \
    "Claude global rules: $HOME/.claude/CLAUDE.md" \
    "Projects and hooks: $PROJECT_ROOT" \
    "Next owner sign-ins:" \
    "  CODEX_HOME=$ROOT_REPO/.codex-membership $ROOT_REPO/.tools/node_modules/.bin/codex login" \
    "  claude auth login"
