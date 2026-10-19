#!/usr/bin/env bash
# Sync the TurboFit repo README from the wiki hub (single source of truth).
# Usage: tools/sync-wiki-readme.sh [wiki_hub_path]
set -euo pipefail
WIKI_HUB="${1:-$HOME/Documents/Projects/Projects/wiki-topics/turbofit/README.md}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$REPO_DIR/README.md"
cp "$WIKI_HUB" "$DEST"
cat >> "$DEST" <<'EOF'

---
> _This README is generated from the [TurboFit wiki](https://github.com/SouthpawIN/agent-wiki/wiki-topics/turbofit/README.md) — the single source of truth. To change it, edit the wiki hub and re-run `tools/sync-wiki-readme.sh`._
EOF
echo "Synced: $WIKI_HUB -> $DEST"
