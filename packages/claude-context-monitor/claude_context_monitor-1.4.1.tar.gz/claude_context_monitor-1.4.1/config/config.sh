#!/bin/bash
# Claude Code Context Monitor Configuration

# Set your Claude plan (pro, max, max5, max20, custom)
export CLAUDE_PLAN="max"

# If using custom plan, set your token limit
# export CLAUDE_MAX_TOKENS="800000"

# Context warning threshold (percentage)
# Triggers handoff when context usage exceeds this
export CONTEXT_THRESHOLD=90

# Status line refresh interval (milliseconds)
export STATUS_REFRESH_INTERVAL=3000

# Token limits by plan (for reference)
# Pro: ~200k tokens
# Max/Max5/Max20: ~600k tokens
# Custom: Set CLAUDE_MAX_TOKENS

# Configuration loaded silently