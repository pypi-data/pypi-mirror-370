---
argument-hint: "[--force]"
description: "Generate project handoff document (global)"
allowed-tools: ["Bash"]
---

Generate a project handoff document to preserve context for other engineers.

I'll create a comprehensive HANDOFF.md document with:
- Current context usage and token counts  
- Git status and recent commits
- Project analysis and next steps
- Setup instructions for continuation
- **Adaptive threshold learning**: Records context % for automatic threshold calibration

**Context Recording**: This command automatically records the current context percentage when triggered, building a dataset of user handoff patterns to gradually improve automatic context management thresholds.

This global command works in any Claude Code project that has the handoff system installed.

Usage: `/handoff` or `/handoff --force`