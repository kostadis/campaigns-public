#!/usr/bin/env bash
# Pull publishable campaign material from the private campaigns repo into
# this public repo. Fetches a fresh shallow, sparse clone from GitHub each
# run; never reads local working copies.
#
# Summaries are selected and named by the campaigns repo's own publisher
# (scripts/publish_sumamries/publish_sumamries) and written to <campaign>/summaries/
# here as the source text, without its refactor/renumbering step.
#
# Usage: scripts/sync-from-campaigns.sh [branch]   (default: main)
#
# <campaign>/summaries/ is owned by this script and replaced wholesale each
# run. Review the diff (git status / git diff) before committing — everything
# here is public.
set -euo pipefail

SRC_REPO="${CAMPAIGNS_REPO:-https://github.com/kostadis/campaigns.git}"
BRANCH="${1:-main}"
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Campaign directories (same name in both repos) whose summaries are published.
CAMPAIGNS=(obelisk out-of-the-abyss)
# Campaigns whose top-level docs/npcs/*.md are copied to <campaign>/npcs/.
NPC_CAMPAIGNS=(obelisk out-of-the-abyss)

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
src="$tmp/campaigns"

patterns=('/scripts/publish_sumamries/publish_sumamries')
for c in "${CAMPAIGNS[@]}"; do
    patterns+=("/$c/summaries/*/session-summary.md"
               "/$c/summaries/*/session_summary.md"
               "/$c/summaries/*/NOT_WRITTEN.txt")
done
for c in "${NPC_CAMPAIGNS[@]}"; do
    patterns+=("/$c/docs/npcs/*.md")
done

echo "Cloning $SRC_REPO ($BRANCH)..."
git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$BRANCH" \
    "$SRC_REPO" "$src"
git -C "$src" sparse-checkout set --no-cone "${patterns[@]}"
rev="$(git -C "$src" rev-parse --short HEAD)"

for c in "${CAMPAIGNS[@]}"; do
    echo
    echo "=== $c: publish_sumamries ==="
    rm -rf "$DEST/$c/summaries"
    mkdir -p "$DEST/$c/summaries"
    # Use the publisher's selection and naming, but write the source bytes
    # directly: skip its refactor step (scene renumbering / reformatting).
    python3 - "$src/scripts/publish_sumamries/publish_sumamries" "$src/$c" "$DEST/$c/summaries" <<'PY'
import importlib.machinery, importlib.util, sys
from pathlib import Path
script, root, out = sys.argv[1:]
loader = importlib.machinery.SourceFileLoader("publish_sumamries", script)
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
planned, *preflight = mod.publication(Path(root))
mod.print_preflight(*preflight)
for name, content in planned.items():
    (Path(out) / name).write_bytes(content)
PY
    echo "$c: wrote $(ls "$DEST/$c/summaries" | wc -l) summaries (unrefactored) to $c/summaries/"
done

for c in "${NPC_CAMPAIGNS[@]}"; do
    # Top level only; summary_native/ holds pipeline working files.
    mkdir -p "$DEST/$c/npcs"
    n=0
    for f in "$src/$c"/docs/npcs/*.md; do
        [[ -e "$f" ]] || continue
        cp "$f" "$DEST/$c/npcs/"
        n=$((n + 1))
    done
    echo "$c: copied $n NPC files to $c/npcs/"
done

echo
echo "Done (source $SRC_REPO @ $rev). Review with: git -C \"$DEST\" status"
