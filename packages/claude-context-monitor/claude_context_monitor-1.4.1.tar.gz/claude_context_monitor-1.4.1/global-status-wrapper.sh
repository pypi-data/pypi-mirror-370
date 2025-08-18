#!/bin/bash
# Global wrapper for Claude Code status line
# Works across all projects by detecting project root from input context

set -euo pipefail

# Load global configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/config.sh" ]]; then
    source "$SCRIPT_DIR/config.sh"
fi

# Get the workspace context from Claude Code if available
input=$(cat)
workspace_dir=""

# Try to extract workspace directory from JSON input
if echo "$input" | jq -e '.workspace.current_dir' >/dev/null 2>&1; then
    workspace_dir=$(echo "$input" | jq -r '.workspace.current_dir')
    cd "$workspace_dir"
fi

# Execute the status script with the detected workspace
MODE="${1:-detailed}"

case "$MODE" in
    "simple")
        exec python3 "$SCRIPT_DIR/status-monitor.py"
        ;;
    *)
        exec python3 "$SCRIPT_DIR/enhanced-status.py" "$MODE"
        ;;
esac