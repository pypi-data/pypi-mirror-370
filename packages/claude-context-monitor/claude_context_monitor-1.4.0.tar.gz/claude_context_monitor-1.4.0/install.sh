#!/bin/bash
# Claude Context Monitor - Installation Script
# Installs real-time context monitoring for all Claude Code projects

set -euo pipefail

echo "🚀 Claude Context Monitor - Installation"
echo "========================================"

# Check requirements
echo "📋 Checking requirements..."

# Check for Claude Code
if ! command -v claude &> /dev/null && [[ ! -d ~/.claude ]]; then
    echo "❌ Claude Code not found. Please install Claude Code first."
    echo "   Visit: https://claude.ai/code"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Check for jq (install if missing)
if ! command -v jq &> /dev/null; then
    echo "📦 Installing jq..."
    if command -v brew &> /dev/null; then
        brew install jq
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v yum &> /dev/null; then
        sudo yum install -y jq
    else
        echo "❌ Please install jq manually: https://stedolan.github.io/jq/"
        exit 1
    fi
fi

echo "✅ Requirements satisfied"

# Create directories
echo "📁 Setting up directories..."
mkdir -p ~/.claude/commands
mkdir -p ~/.claude

# Get installation directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install core files
echo "📦 Installing core files..."
cp "$SCRIPT_DIR/enhanced-status.py" ~/.claude/
cp "$SCRIPT_DIR/status-monitor.py" ~/.claude/
cp "$SCRIPT_DIR/intelligent_plan_detector.py" ~/.claude/
cp "$SCRIPT_DIR/handoff_tracker.py" ~/.claude/
cp "$SCRIPT_DIR/global-status-wrapper.sh" ~/.claude/
cp "$SCRIPT_DIR/configure-global-status.sh" ~/.claude/
cp "$SCRIPT_DIR/handoff.md" ~/.claude/commands/

# Set up configuration
if [[ ! -f ~/.claude/config.sh ]]; then
    echo "⚙️ Setting up configuration..."
    cp "$SCRIPT_DIR/config.sh" ~/.claude/
else
    echo "📝 Configuration file exists, keeping current settings"
fi

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x ~/.claude/enhanced-status.py
chmod +x ~/.claude/status-monitor.py
chmod +x ~/.claude/handoff_tracker.py
chmod +x ~/.claude/global-status-wrapper.sh
chmod +x ~/.claude/configure-global-status.sh

# Create command line tool (optional, only if user has sudo access)
echo "🛠️ Installing command line tool..."
if [[ -w /usr/local/bin ]] || command -v sudo &> /dev/null; then
    if sudo -n true 2>/dev/null; then
        # User has passwordless sudo
        sudo tee /usr/local/bin/claude-context-config > /dev/null << 'EOF'
#!/bin/bash
exec ~/.claude/configure-global-status.sh "$@"
EOF
        sudo chmod +x /usr/local/bin/claude-context-config
        echo "✅ Global command 'claude-context-config' installed"
    else
        echo "⚠️  Skipping global command installation (requires sudo)"
        echo "💡 Use ~/.claude/configure-global-status.sh instead"
    fi
else
    echo "⚠️  /usr/local/bin not writable, skipping global command"
    echo "💡 Use ~/.claude/configure-global-status.sh instead"
fi

# Configure Claude Code settings
echo "📝 Configuring Claude Code..."

# Backup existing settings if they exist
if [[ -f ~/.claude/settings.json ]]; then
    echo "💾 Backing up existing settings..."
    cp ~/.claude/settings.json ~/.claude/settings.backup.$(date +%Y%m%d_%H%M%S).json
fi

# Create or update settings
if [[ ! -f ~/.claude/settings.json ]]; then
    cat > ~/.claude/settings.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "statusLine": {
    "type": "command",
    "command": "~/.claude/global-status-wrapper.sh detailed",
    "refreshInterval": 3000
  }
}
EOF
else
    # Update existing settings
    jq '.statusLine = {
        "type": "command",
        "command": "~/.claude/global-status-wrapper.sh detailed", 
        "refreshInterval": 3000
    }' ~/.claude/settings.json > ~/.claude/settings.json.tmp
    mv ~/.claude/settings.json.tmp ~/.claude/settings.json
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Restart Claude Code to activate the status line"
echo "2. Your status line will show: 💻 user:project │ 🔵 16.3% (98K) │ 🌿main ± │ 🎯MAX"
echo "3. Use /handoff command in any Claude Code project"
echo "4. Features intelligent plan detection - no configuration needed!"
echo ""
echo "📖 Configuration (optional):"
if command -v claude-context-config &> /dev/null; then
    echo "- Status: claude-context-config info"
    echo "- Switch modes: claude-context-config compact|detailed|simple"
else
    echo "- Status: ~/.claude/configure-global-status.sh info"
    echo "- Switch modes: ~/.claude/configure-global-status.sh compact|detailed|simple"
fi
echo ""
echo "🎉 Happy coding with better context awareness!"