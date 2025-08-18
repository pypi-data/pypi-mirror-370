"""
Claude Context Monitor - Advanced context monitoring for Claude Code

A comprehensive monitoring system that provides:
- Real-time context usage tracking
- Intelligent plan detection
- Adaptive threshold learning
- Global status line integration
"""

__version__ = "1.0.0"
__author__ = "Xiao Constantine"

from .status import EnhancedStatus, StatusMonitor
from .plan_detector import PlanDetector, detect_claude_plan
from .handoff import HandoffTracker

__all__ = [
    "EnhancedStatus",
    "StatusMonitor",
    "PlanDetector",
    "detect_claude_plan",
    "HandoffTracker",
]
