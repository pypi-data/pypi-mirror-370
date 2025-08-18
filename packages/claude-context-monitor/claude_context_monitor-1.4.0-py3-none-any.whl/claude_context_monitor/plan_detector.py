#!/usr/bin/env python3
"""
Intelligent Claude Plan Detection with Adaptive Thresholds
"""

import json
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import os


class PlanDetector:
    """Intelligent plan detection using P90 analysis of historical usage"""

    # Known Claude plan limits
    PLAN_LIMITS = {
        "pro": 200000,  # Claude Pro
        "max": 600000,  # Claude Max (legacy)
        "max5": 600000,  # Claude Max 5
        "max20": 600000,  # Claude Max 20
    }

    # Confidence thresholds for plan detection
    CONFIDENCE_THRESHOLD = 0.8
    MIN_SESSIONS_FOR_DETECTION = 5
    ANALYSIS_WINDOW_HOURS = 192  # 8 days

    # Handoff tracking
    HANDOFF_DATA_FILE = Path.home() / ".claude" / "handoff_context_data.json"

    def __init__(self, project_root: Path = None):
        """Initialize with project root for finding session data"""
        self.project_root = project_root or Path.cwd()
        self.handoff_data_file = self.HANDOFF_DATA_FILE

    def get_session_files(self) -> List[Path]:
        """Find all relevant JSONL session files for analysis"""
        claude_projects_dir = Path.home() / ".claude" / "projects"

        # Find current project session directory
        current_project = str(self.project_root).replace("/", "-").replace(".", "-")
        project_session_dir = claude_projects_dir / current_project

        # Fallback: search by project name
        if not project_session_dir.exists():
            project_name = self.project_root.name
            for dir_path in claude_projects_dir.glob(f"*{project_name}*"):
                if dir_path.is_dir():
                    project_session_dir = dir_path
                    break

        if not project_session_dir.exists():
            return []

        # Get all JSONL files, sorted by modification time
        jsonl_files = sorted(
            project_session_dir.glob("*.jsonl"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        return jsonl_files[:10]  # Analyze last 10 sessions max

    def extract_token_usage_history(self, jsonl_files: List[Path]) -> List[int]:
        """Extract token usage patterns from session files"""
        token_usage_history = []
        cutoff_time = datetime.now().replace(tzinfo=None) - timedelta(
            hours=self.ANALYSIS_WINDOW_HOURS
        )

        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, "r") as f:
                    lines = f.readlines()

                session_max_tokens = 0

                for line in lines:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line.strip())

                        # Check if entry is within our analysis window
                        if "timestamp" in entry:
                            entry_time = datetime.fromisoformat(
                                entry["timestamp"].replace("Z", "")
                            )
                            if entry_time < cutoff_time:
                                continue

                        # Extract usage data
                        if "message" in entry and isinstance(entry["message"], dict):
                            usage = entry["message"].get("usage", {})
                            if usage:
                                input_t = usage.get("input_tokens", 0)
                                output_t = usage.get("output_tokens", 0)
                                cache_read = usage.get("cache_read_input_tokens", 0)
                                cache_create = usage.get(
                                    "cache_creation_input_tokens", 0
                                )
                                total_tokens = (
                                    input_t + output_t + cache_read + cache_create
                                )

                                session_max_tokens = max(
                                    session_max_tokens, total_tokens
                                )

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

                if session_max_tokens > 1000:  # Only include meaningful sessions
                    token_usage_history.append(session_max_tokens)

            except (IOError, OSError):
                continue

        return token_usage_history

    def calculate_p90_limit(self, token_history: List[int]) -> Optional[int]:
        """Calculate 90th percentile token limit from usage history"""
        if len(token_history) < self.MIN_SESSIONS_FOR_DETECTION:
            return None

        try:
            # Calculate 90th percentile
            p90_limit = statistics.quantiles(token_history, n=10)[8]  # 90th percentile

            # Round up to nearest 10K for cleaner limits
            return int((p90_limit + 9999) // 10000 * 10000)

        except (statistics.StatisticsError, IndexError):
            return None

    def detect_plan_from_limit(self, observed_limit: int) -> Tuple[str, float]:
        """
        Detect Claude plan based on observed P90 limit
        Returns (plan_name, confidence_score)
        """
        # Special case: if observed limit exceeds all known limits,
        # assume it's a higher tier plan or custom limit
        if observed_limit > max(self.PLAN_LIMITS.values()):
            return "max", 0.9  # High confidence it's at least Max

        # If observed limit is close to or exceeds Pro limit, likely Max plan
        if observed_limit >= self.PLAN_LIMITS["pro"] * 0.75:  # Using >=75% of Pro limit
            return "max", 0.85  # High confidence it's Max plan

        # For lower usage, determine which plan fits best
        best_match = "pro"
        best_confidence = 0.0

        for plan_name, plan_limit in self.PLAN_LIMITS.items():
            if observed_limit <= plan_limit:
                # Calculate confidence based on how much of the limit is being used
                usage_ratio = observed_limit / plan_limit

                # Higher confidence if we're using a significant portion of the limit
                if usage_ratio >= 0.1:  # At least 10% usage
                    confidence = min(usage_ratio * 1.2, 1.0)  # Boost confidence
                else:
                    confidence = 0.3  # Low confidence for very low usage

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = plan_name

        return best_match, best_confidence

    def record_handoff_context(
        self, context_percentage: float, total_tokens: int, project_name: str = None
    ) -> None:
        """Record context percentage when handoff is triggered for threshold learning"""
        try:
            project_name = project_name or self.project_root.name
            timestamp = datetime.now().isoformat()

            # Load existing data
            handoff_data = self.load_handoff_data()

            # Add new handoff record
            if project_name not in handoff_data:
                handoff_data[project_name] = []

            handoff_record = {
                "timestamp": timestamp,
                "context_percentage": context_percentage,
                "total_tokens": total_tokens,
                "project": project_name,
            }

            handoff_data[project_name].append(handoff_record)

            # Keep only recent 50 handoffs per project
            handoff_data[project_name] = handoff_data[project_name][-50:]

            # Save updated data
            self.save_handoff_data(handoff_data)

        except Exception:
            # Fail silently - don't break functionality if handoff tracking fails
            pass

    def load_handoff_data(self) -> Dict[str, List[Dict]]:
        """Load handoff context data from file"""
        try:
            if self.handoff_data_file.exists():
                with open(self.handoff_data_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_handoff_data(self, data: Dict[str, List[Dict]]) -> None:
        """Save handoff context data to file"""
        try:
            # Ensure directory exists
            self.handoff_data_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.handoff_data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_adaptive_threshold(self, project_name: str = None) -> float:
        """Calculate adaptive threshold based on historical handoff patterns"""
        try:
            project_name = project_name or self.project_root.name
            handoff_data = self.load_handoff_data()

            if project_name not in handoff_data or len(handoff_data[project_name]) < 3:
                # Default threshold if not enough data
                return float(os.environ.get("CONTEXT_THRESHOLD", 90))

            # Get recent handoff percentages (last 20)
            recent_handoffs = handoff_data[project_name][-20:]
            percentages = [h["context_percentage"] for h in recent_handoffs]

            # Calculate adaptive threshold (average of handoffs minus safety margin)
            avg_handoff_percentage = sum(percentages) / len(percentages)
            safety_margin = 5  # 5% safety margin
            adaptive_threshold = max(
                75, avg_handoff_percentage - safety_margin
            )  # Min 75%

            return min(95, adaptive_threshold)  # Max 95%

        except Exception:
            return float(os.environ.get("CONTEXT_THRESHOLD", 90))

    def get_handoff_stats(self, project_name: str = None) -> Dict[str, Any]:
        """Get handoff statistics for analysis"""
        try:
            project_name = project_name or self.project_root.name
            handoff_data = self.load_handoff_data()

            if project_name not in handoff_data or not handoff_data[project_name]:
                return {
                    "handoff_count": 0,
                    "avg_handoff_percentage": None,
                    "adaptive_threshold": float(
                        os.environ.get("CONTEXT_THRESHOLD", 90)
                    ),
                    "last_handoff": None,
                }

            handoffs = handoff_data[project_name]
            percentages = [h["context_percentage"] for h in handoffs]

            return {
                "handoff_count": len(handoffs),
                "avg_handoff_percentage": sum(percentages) / len(percentages),
                "min_handoff_percentage": min(percentages),
                "max_handoff_percentage": max(percentages),
                "adaptive_threshold": self.get_adaptive_threshold(project_name),
                "last_handoff": handoffs[-1]["timestamp"] if handoffs else None,
            }

        except Exception:
            return {
                "handoff_count": 0,
                "avg_handoff_percentage": None,
                "adaptive_threshold": float(os.environ.get("CONTEXT_THRESHOLD", 90)),
                "last_handoff": None,
            }

    def get_intelligent_plan_detection(self) -> Dict[str, Any]:
        """
        Main method: Intelligently detect Claude plan using P90 analysis
        Returns comprehensive detection results
        """
        # Check for manual override first (moved here for consistency)
        manual_plan = os.environ.get("CLAUDE_PLAN", "").lower()
        if manual_plan in self.PLAN_LIMITS:
            return {
                "detected_plan": manual_plan,
                "confidence": 1.0,
                "method": "manual_override",
                "token_limit": self.PLAN_LIMITS[manual_plan],
                "sessions_analyzed": 0,
                "reason": f"CLAUDE_PLAN environment variable set to {manual_plan}",
            }

        session_files = self.get_session_files()

        if not session_files:
            return {
                "detected_plan": "pro",
                "confidence": 0.0,
                "method": "fallback",
                "p90_limit": None,
                "token_limit": self.PLAN_LIMITS["pro"],
                "sessions_analyzed": 0,
                "reason": "No session files found",
            }

        token_history = self.extract_token_usage_history(session_files)

        if len(token_history) < self.MIN_SESSIONS_FOR_DETECTION:
            # Check if ANY session exceeded PRO limits
            max_tokens_seen = max(token_history) if token_history else 0
            if max_tokens_seen > self.PLAN_LIMITS["pro"]:
                return {
                    "detected_plan": "max",
                    "confidence": 0.95,
                    "method": "exceeded_pro_limit",
                    "p90_limit": None,
                    "token_limit": self.PLAN_LIMITS["max"],
                    "sessions_analyzed": len(token_history),
                    "max_tokens_seen": max_tokens_seen,
                    "reason": f"Session exceeded PRO limit ({max_tokens_seen:,} > 200,000)",
                }

            return {
                "detected_plan": "pro",
                "confidence": 0.2,
                "method": "insufficient_data",
                "p90_limit": None,
                "token_limit": self.PLAN_LIMITS["pro"],
                "sessions_analyzed": len(token_history),
                "reason": f"Only {len(token_history)} sessions found, need {self.MIN_SESSIONS_FOR_DETECTION}",
            }

        p90_limit = self.calculate_p90_limit(token_history)

        if p90_limit is None:
            return {
                "detected_plan": "pro",
                "confidence": 0.1,
                "method": "calculation_failed",
                "p90_limit": None,
                "token_limit": self.PLAN_LIMITS["pro"],
                "sessions_analyzed": len(token_history),
                "reason": "P90 calculation failed",
            }

        detected_plan, confidence = self.detect_plan_from_limit(p90_limit)

        return {
            "detected_plan": detected_plan,
            "confidence": confidence,
            "method": "p90_analysis",
            "p90_limit": p90_limit,
            "token_limit": self.PLAN_LIMITS.get(detected_plan, p90_limit),
            "sessions_analyzed": len(token_history),
            "max_observed_usage": max(token_history),
            "min_observed_usage": min(token_history),
            "avg_observed_usage": sum(token_history) // len(token_history),
            "reason": "Statistical analysis of recent usage patterns",
            "handoff_stats": self.get_handoff_stats(),
            "adaptive_threshold": self.get_adaptive_threshold(),
        }


def detect_claude_plan(project_root: Path = None) -> Dict[str, Any]:
    """Convenience function for plan detection"""
    detector = PlanDetector(project_root)
    return detector.get_intelligent_plan_detection()
