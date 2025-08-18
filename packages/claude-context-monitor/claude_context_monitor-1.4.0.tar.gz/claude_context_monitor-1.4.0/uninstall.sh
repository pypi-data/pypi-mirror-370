#!/bin/bash
# Claude Context Monitor - Uninstallation Script

set -euo pipefail

echo "🗑️ Claude Context Monitor - Uninstaller"
echo "========================================"

# Confirm uninstallation
read -p "Are you sure you want to uninstall Claude Context Monitor? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Uninstallation cancelled"
    exit 0
fi

echo "🧹 Removing Claude Context Monitor..."

# Backup settings before removing
if [[ -f ~/.claude/settings.json ]]; then
    echo "💾 Backing up Claude Code settings..."
    cp ~/.claude/settings.json ~/.claude/settings.backup.before-uninstall.$(date +%Y%m%d_%H%M%S).json
fi

# Remove status line from settings
echo "📝 Removing status line configuration..."
if [[ -f ~/.claude/settings.json ]] && command -v jq &> /dev/null; then
    jq 'del(.statusLine)' ~/.claude/settings.json > ~/.claude/settings.json.tmp
    mv ~/.claude/settings.json.tmp ~/.claude/settings.json
fi

# Remove installed files
echo "🗂️ Removing installed files..."
rm -f ~/.claude/enhanced-status.py
rm -f ~/.claude/status-monitor.py
rm -f ~/.claude/global-status-wrapper.sh
rm -f ~/.claude/configure-global-status.sh
rm -f ~/.claude/config.sh
rm -f ~/.claude/commands/handoff.md

# Remove command line tool
echo "🛠️ Removing command line tool..."
sudo rm -f /usr/local/bin/claude-context-config

echo ""
echo "✅ Uninstallation complete!"
echo ""
echo "📋 What was removed:"
echo "- Status line monitoring scripts"
echo "- Global /handoff command"
echo "- Status line configuration from Claude Code"
echo "- Command line configuration tool"
echo ""
echo "📁 Kept (for safety):"
echo "- Claude Code settings backup in ~/.claude/"
echo "- Your Claude Code projects and data"
echo ""
echo "🔄 Restart Claude Code to see changes"