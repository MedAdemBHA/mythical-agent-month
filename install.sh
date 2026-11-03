#!/usr/bin/env bash
# Install the mythical-agent-month skill for one or more coding agents.
#
#   ./install.sh                     # Claude Code, personal (all projects)
#   ./install.sh codex cursor        # several agents
#   ./install.sh all                 # every supported agent
#   ./install.sh all --project       # into the current project instead of your home folder
#
# One-liner (no clone needed):
#   curl -fsSL https://raw.githubusercontent.com/MedAdemBHA/mythical-agent-month/main/install.sh | bash -s -- all
set -euo pipefail

NAME="mythical-agent-month"
REPO="https://github.com/MedAdemBHA/mythical-agent-month.git"

project=0
agents=()
for a in "$@"; do
  case "$a" in
    --project) project=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) agents+=("$a") ;;
  esac
done
[ ${#agents[@]} -eq 0 ] && agents=(claude)
[ "${agents[0]}" = "all" ] && agents=(claude codex cursor gemini copilot)

# Find the skill folder: next to this script, or fetch the repo.
src=""
here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -n "$here" ] && [ -f "$here/skills/$NAME/SKILL.md" ]; then
  src="$here/skills/$NAME"
else
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  git clone -q --depth 1 "$REPO" "$tmp/repo"
  src="$tmp/repo/skills/$NAME"
fi

# Skills folders per agent: <personal> <project>
dirs_for() {
  case "$1" in
    claude)  echo "$HOME/.claude/skills .claude/skills" ;;
    codex)   echo "$HOME/.agents/skills .agents/skills" ;;
    cursor)  echo "$HOME/.cursor/skills .cursor/skills" ;;
    gemini)  echo "$HOME/.gemini/skills .gemini/skills" ;;
    copilot) echo "$HOME/.copilot/skills .github/skills" ;;
    *) echo "" ;;
  esac
}

for agent in "${agents[@]}"; do
  read -r personal proj <<<"$(dirs_for "$agent")"
  if [ -z "${personal:-}" ]; then
    echo "unknown agent: $agent (use claude, codex, cursor, gemini, copilot or all)" >&2
    exit 1
  fi
  dest="$personal"; [ $project -eq 1 ] && dest="$proj"
  mkdir -p "$dest"
  rm -rf "${dest:?}/$NAME"
  cp -R "$src" "$dest/$NAME"
  echo "✓ $agent → $dest/$NAME"
done
echo "Done. Ask your agent: \"how long will this take?\""
