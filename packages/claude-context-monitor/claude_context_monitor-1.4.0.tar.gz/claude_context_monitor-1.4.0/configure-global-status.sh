#!/bin/bash
# Configure global Claude Code status line mode

set -euo pipefail

SETTINGS_FILE="$HOME/.claude/settings.json"

case "${1:-detailed}" in
    "compact")
        echo "🔧 Setting global status line to compact mode..."
        jq '.statusLine.command = "~/.claude/global-status-wrapper.sh compact"' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
        mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "✅ Global status line: 🔵0% ⚡main [M]"
        ;;
        
    "detailed")
        echo "🔧 Setting global status line to detailed mode..."
        jq '.statusLine.command = "~/.claude/global-status-wrapper.sh detailed"' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
        mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "✅ Global status line: 🔵 Context: 0.3% (2K/600K) | ⚡main | MAX"
        ;;
        
    "simple")
        echo "🔧 Setting global status line to simple mode..."
        jq '.statusLine.command = "~/.claude/global-status-wrapper.sh simple"' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
        mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "✅ Global status line: 🔵 0.3% (2K/600K) [MAX] LOW"
        ;;
        
    "off")
        echo "🔧 Disabling global status line..."
        jq 'del(.statusLine)' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
        mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "✅ Global status line disabled"
        ;;
        
    "info")
        echo "📊 Current Global Status Line Configuration:"
        echo "────────────────────────────────────────────"
        if jq -e '.statusLine' "$SETTINGS_FILE" >/dev/null 2>&1; then
            echo "Status: ENABLED"
            echo "Command: $(jq -r '.statusLine.command' "$SETTINGS_FILE")"
            echo "Refresh: $(jq -r '.statusLine.refreshInterval // "default"' "$SETTINGS_FILE")ms"
            echo ""
            echo "🧪 Test output:"
            ~/.claude/global-status-wrapper.sh detailed <<< '{"workspace":{"current_dir":"'$(pwd)'"}}'
        else
            echo "Status: DISABLED"
        fi
        ;;
        
    *)
        echo "Usage: $0 [compact|detailed|simple|off|info]"
        echo ""
        echo "Modes:"
        echo "  compact  - 🔵0% ⚡main [M]"
        echo "  detailed - 🔵 Context: 0.3% (2K/600K) | ⚡main | MAX"
        echo "  simple   - 🔵 0.3% (2K/600K) [MAX] LOW"
        echo "  off      - Disable status line globally"
        echo "  info     - Show current configuration and test"
        echo ""
        echo "Global config applies to ALL Claude Code projects!"
        exit 1
        ;;
esac

echo "🔄 Restart Claude Code to see changes globally"