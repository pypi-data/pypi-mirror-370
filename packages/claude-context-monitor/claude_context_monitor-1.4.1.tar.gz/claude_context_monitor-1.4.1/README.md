# Claude Context Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-blue.svg)](https://claude.ai/code)
[![PyPI version](https://badge.fury.io/py/claude-context-monitor.svg)](https://badge.fury.io/py/claude-context-monitor)

**Advanced context monitoring and adaptive threshold learning for Claude Code**

## 🚀 Features

- **Real-time status line** showing context usage in all projects
- **Intelligent plan detection** using P90 analysis - no manual configuration needed!
- **Automatic handoff generation** when approaching context limits  
- **Claude Max/Pro support** with appropriate token limits
- **Global `/handoff` command** available everywhere
- **Git integration** showing branch and status
- **Zero configuration** for new projects

## 📺 Demo

Your Claude Code status line will show:
```
💻 user:project │ 🔵 16.3% (98K) │ 🌿main ± │ 🎯MAX
```

## ⚡ Installation

### 🚀 Recommended: UV + UVX (Modern Python)
```bash
# Install with uvx (no global installation needed)
uvx claude-context-monitor status

# Or install globally
uv tool install claude-context-monitor

# Use commands anywhere
claude-context status
ccm handoff --record
```

### 📦 Traditional pip
```bash
pip install claude-context-monitor
claude-context install
```

### 🔧 Legacy Shell Install
```bash
curl -fsSL https://raw.githubusercontent.com/XiaoConstantine/claude-context-monitor/main/install.sh | bash
```

### Development Install
```bash
git clone https://github.com/XiaoConstantine/claude-context-monitor.git
cd claude-context-monitor
./install.sh
```

## 🎯 Usage

### CLI Commands

```bash
# Status monitoring
claude-context status              # Current context status  
claude-context status -f json      # JSON output
ccm status -f compact             # Compact format (short alias)

# Plan detection
claude-context plan               # Detect Claude plan automatically
claude-context plan --json       # JSON output

# Handoff tracking & adaptive learning  
claude-context handoff --record  # Record handoff for threshold learning
claude-context handoff --stats   # Show historical handoff statistics
claude-context handoff --summary # Get summary for documents

# Configuration
claude-context config --show     # Show current config
claude-context config --set CLAUDE_PLAN=max  # Set values
claude-context config --get CONTEXT_THRESHOLD

# Installation (legacy compatibility)
claude-context install           # Install to ~/.claude
claude-context install --force   # Force reinstall
```

### Global Claude Commands
```
/handoff          # Generate handoff document (auto-records context %)
/handoff --force  # Force generation
```

### Automatic Features
- **Real-time status**: Shows in Claude Code status line
- **Adaptive thresholds**: Learns from your handoff patterns  
- **Plan detection**: Automatically detects Pro/Max plans
- **Git integration**: Shows branch and dirty status

# Manual plan override (optional - auto-detection is recommended)
export CLAUDE_PLAN=max    # Force Claude Max (600K tokens)
export CLAUDE_PLAN=pro    # Force Claude Pro (200K tokens)
# Leave unset for intelligent auto-detection
```

## 🧠 Intelligent Plan Detection

The monitor automatically detects your Claude plan using **P90 analysis** of your usage history:

- **Analyzes** your last 8 days of token usage patterns
- **Calculates** 90th percentile usage from recent sessions  
- **Detects** if you're on Pro (200K) or Max (600K) plan with 85% confidence
- **Falls back** to conservative Pro limits if insufficient data

No manual configuration needed! The system learns from your actual usage patterns.

```json
{
  "detected_plan": "max",
  "confidence": 0.85,
  "method": "p90_analysis", 
  "p90_limit": 160000,
  "token_limit": 600000,
  "sessions_analyzed": 8
}
```

## 🔧 How It Works

1. **Real-time monitoring**: Reads token usage from Claude Code's session files (`~/.claude/projects/`)
2. **Intelligent detection**: Uses P90 analysis to automatically detect your Claude plan
3. **Smart limits**: Adjusts thresholds for Claude Max (600K) vs Pro (200K) tokens
4. **Auto-handoff**: Generates detailed handoff documents at 90% usage
5. **Git integration**: Shows current branch and dirty status

## 📊 Status Indicators

### Context Usage Colors
- 🔵 **Low** (0-49%): Plenty of context remaining
- 🟢 **OK** (50-74%): Context usage moderate  
- 🟡 **High** (75-89%): Approaching context limit
- 🔴 **Critical** (90%+): Handoff generation triggered

### Git Status
- 📁 **Clean**: No uncommitted changes
- ⚡ **Dirty**: Uncommitted changes present

## 📋 Requirements

- **Claude Code**: Latest version with statusLine support
- **Python 3.8+**: For status monitoring scripts
- **jq**: For JSON configuration management
- **Git**: For project status detection (optional)

## 📖 Documentation

- [Installation Guide](docs/INSTALL.md)
- [Configuration Reference](docs/CONFIG.md)  
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [Claude Code](https://claude.ai/code) community
- Inspired by the need for better context management in AI-assisted development
- P90 analysis approach inspired by [Maciek's Claude Code Usage Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)

---
