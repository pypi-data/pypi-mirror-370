# Adaptive Threshold Learning

The Claude Context Monitor now includes **adaptive threshold learning** that automatically adjusts context warning thresholds based on your actual handoff patterns.

## How It Works

### 1. Handoff Recording
Every time you use the `/handoff` command, the system automatically:
- Records your current context percentage
- Stores the data with timestamp and project information
- Builds a historical dataset of your handoff patterns

### 2. Adaptive Calculation
The system calculates an adaptive threshold using:
```
Adaptive Threshold = Average Handoff % - Safety Margin (5%)
```

**Example**: If you typically handoff at 80%, 85%, and 90% context usage:
- Average: 85%
- Safety margin: 5%
- **Adaptive threshold: 80%**

### 3. Automatic Application
- Minimum threshold: 75% (prevents too-aggressive warnings)
- Maximum threshold: 95% (ensures warnings still trigger)
- Requires at least 3 handoffs to start learning

## Visual Indicators

### Status Line
When adaptive threshold differs from your configured threshold:
```bash
💻 xiao:project │ 🔵 82.3% (450K) │ 🌿main │ 🎯MAX (→80%)
                                                   ↑
                                        Adaptive threshold
```

### Handoff Command Output
```bash
🎯 Handoff recorded at 85.2% context usage
📊 Tokens: 512,000 / 600,000
🔧 Adaptive threshold: 80%
📈 Historical average: 84.1% (5 handoffs)
```

## Manual Commands

### Record Handoff Context
```bash
# Record current context for learning
~/.claude/handoff_tracker.py

# Get detailed JSON output
~/.claude/handoff_tracker.py --record
```

### View Context Info
```bash
# Current context usage
~/.claude/handoff_tracker.py --context

# Handoff summary for documents
~/.claude/handoff_tracker.py --summary
```

## Benefits

1. **Personalized**: Learns your specific workflow patterns
2. **Project-aware**: Different thresholds per project
3. **Automatic**: No manual configuration needed
4. **Safe**: Conservative defaults with minimum thresholds
5. **Transparent**: Clear indicators when active

## Data Storage

Handoff data is stored in:
```
~/.claude/handoff_context_data.json
```

Format:
```json
{
  "project-name": [
    {
      "timestamp": "2025-08-15T11:45:23.123456",
      "context_percentage": 85.2,
      "total_tokens": 512000,
      "project": "my-project"
    }
  ]
}
```

## Privacy & Control

- **Local only**: All data stays on your machine
- **Project-scoped**: No cross-project data sharing  
- **User-driven**: Only learns from your `/handoff` commands
- **Deletable**: Remove `handoff_context_data.json` to reset

## Integration with Existing Features

- **Intelligent Plan Detection**: Works with auto-detected Claude plans
- **Status Monitoring**: Shows adaptive thresholds in status lines
- **Global Commands**: Available across all Claude Code projects
- **Handoff Documents**: Context info included in HANDOFF.md files

## Example Learning Process

```bash
# First few handoffs - using default 90% threshold
/handoff  # at 88% → recorded
/handoff  # at 85% → recorded  
/handoff  # at 82% → recorded

# System learns: average = 85%, safety margin = 5%
# New adaptive threshold: 80%

# Status line now shows:
💻 user:project │ 🟡 81.5% │ 🌿main │ 🎯MAX (→80%)
                    ↑ Warning triggered at 80% instead of 90%
```

This creates a **feedback loop** where the system becomes more aligned with your actual usage patterns over time.