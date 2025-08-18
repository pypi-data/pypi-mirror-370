#!/usr/bin/env python3
"""
Handoff Context Tracker
Records context percentages for adaptive threshold learning
"""

from pathlib import Path

from .status import EnhancedStatus
from .plan_detector import PlanDetector


class HandoffTracker:
    """Tracks handoff context for adaptive threshold learning"""

    def __init__(self, project_root=None):
        """Initialize with project root"""
        self.project_root = project_root or Path.cwd()
        self.project_name = self.project_root.name
        self.detector = PlanDetector(self.project_root)
        self.status = EnhancedStatus(self.project_root)

    def get_current_context(self):
        """Get current context usage"""
        return self.status.get_context_usage()

    def record_handoff(self):
        """Record handoff with current context percentage"""
        try:
            # Get current context usage
            context_data = self.get_current_context()

            if context_data.get("tokens_used", 0) == 0:
                return {
                    "success": False,
                    "error": "No context usage found",
                    "recorded": False,
                }

            # Record the handoff
            self.detector.record_handoff_context(
                context_percentage=context_data["usage_percent"],
                total_tokens=context_data["tokens_used"],
                project_name=self.project_name,
            )

            # Get adaptive threshold info
            adaptive_threshold = self.detector.get_adaptive_threshold()
            handoff_stats = self.detector.get_handoff_stats()

            return {
                "success": True,
                "recorded": True,
                "context_percentage": round(context_data["usage_percent"], 1),
                "total_tokens": context_data["tokens_used"],
                "max_tokens": context_data.get("max_tokens", 200000),
                "project": self.project_name,
                "adaptive_threshold": adaptive_threshold,
                "handoff_count": handoff_stats.get("handoff_count", 0),
                "avg_handoff_percentage": handoff_stats.get("avg_handoff_percentage"),
                "previous_threshold": float(
                    Path.home()
                    .joinpath(".claude/config.sh")
                    .read_text()
                    .split("CONTEXT_THRESHOLD=")[1]
                    .split("\n")[0]
                    if Path.home().joinpath(".claude/config.sh").exists()
                    and "CONTEXT_THRESHOLD="
                    in Path.home().joinpath(".claude/config.sh").read_text()
                    else 90
                ),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "recorded": False}

    def get_handoff_summary(self):
        """Get summary of handoff tracking for inclusion in handoff documents"""
        try:
            result = self.record_handoff()

            if not result.get("success", False):
                return f"\n## Context Tracking\n❌ Failed to record handoff: {result.get('error', 'Unknown error')}\n"

            # Format context info for handoff document
            context_info = f"""
## Context Usage at Handoff
- **Current Usage**: {result["context_percentage"]}% ({result["total_tokens"]:,} tokens)
- **Token Limit**: {result["max_tokens"]:,} tokens  
- **Project**: {result["project"]}

## Adaptive Threshold Learning
- **Current Threshold**: {result["previous_threshold"]}%
- **Adaptive Threshold**: {result["adaptive_threshold"]}%
- **Handoff Count**: {result["handoff_count"]}"""

            if result.get("avg_handoff_percentage"):
                context_info += f"\n- **Average Handoff %**: {result['avg_handoff_percentage']:.1f}%"

            context_info += f"""

*🤖 This handoff was recorded at {result["context_percentage"]}% context usage to help calibrate automatic context management thresholds.*
"""

            return context_info

        except Exception as e:
            return f"\n## Context Tracking\n❌ Error: {str(e)}\n"

    def get_handoff_stats(self):
        """Get handoff statistics"""
        return self.detector.get_handoff_stats(self.project_name)
