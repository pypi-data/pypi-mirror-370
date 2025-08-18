#!/usr/bin/env python3
"""
Status monitoring modules for Claude Context Monitor
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from .turn_tracker import TurnTracker


class BaseStatus:
    """Base class for status monitoring"""

    def __init__(self, project_root=None):
        """Initialize with project root for finding session data"""
        self.project_root = project_root or self.find_project_root()
        self.turn_tracker = TurnTracker()

    @staticmethod
    def find_project_root():
        """Find the project root by looking for git or .claude directory"""
        current = Path.cwd()

        # First, prefer current directory if it's a git repo
        if (current / ".git").exists():
            return current

        # Look for git repos in current path
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent

        # Fallback: Look for .claude directory (but prefer closer ones)
        for parent in [current] + list(current.parents):
            if (parent / ".claude").exists():
                return parent

        return current

    def get_session_files(self):
        """Find the current session's JSONL files"""
        claude_projects_dir = Path.home() / ".claude" / "projects"

        # Find project session directory
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

        # Get JSONL files sorted by access time (most recent first)
        jsonl_files = sorted(
            project_session_dir.glob("*.jsonl"),
            key=lambda x: x.stat().st_atime,
            reverse=True,
        )

        return jsonl_files

    def get_context_usage(self):
        """Get current context usage from Claude JSONL files"""
        try:
            jsonl_files = self.get_session_files()

            if not jsonl_files:
                return {"usage_percent": 0, "tokens_used": 0, "max_tokens": 200000}

            recent_file = jsonl_files[0]

            with open(recent_file, "r") as f:
                lines = f.readlines()

            # Get the ACTUAL current context from the latest entry
            current_context = 0
            has_recent_usage = False
            turn_tokens = 0
            turn_number = 0

            # Get the last valid usage entry for current context
            for line in reversed(lines):
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        if "message" in entry and isinstance(entry["message"], dict):
                            usage = entry["message"].get("usage", {})
                            if usage and (
                                usage.get("input_tokens", 0) > 0
                                or usage.get("output_tokens", 0) > 0
                            ):
                                input_t = usage.get("input_tokens", 0)
                                output_t = usage.get("output_tokens", 0)
                                cache_read = usage.get("cache_read_input_tokens", 0)
                                cache_create = usage.get(
                                    "cache_creation_input_tokens", 0
                                )

                                current_context = (
                                    input_t + output_t + cache_read + cache_create
                                )

                                # Update turn tracker
                                timestamp = datetime.now()
                                if "timestamp" in entry:
                                    try:
                                        timestamp = datetime.fromisoformat(
                                            entry["timestamp"]
                                        )
                                    except:
                                        pass

                                turn_tokens, turn_number = self.turn_tracker.update(
                                    timestamp=timestamp,
                                    input_tokens=input_t,
                                    output_tokens=output_t,
                                    cache_read=cache_read,
                                    cache_create=cache_create,
                                    total_cumulative=current_context,
                                )

                                has_recent_usage = True
                                break
                    except:
                        continue

            # If no recent usage found in current file, this might be a fresh session
            if (
                not has_recent_usage and len(lines) < 10
            ):  # Small file = likely fresh session
                current_context = 10  # Very minimal baseline for fresh sessions

            # Get plan limits with intelligent detection
            from .plan_detector import detect_claude_plan

            plan_info = detect_claude_plan(self.project_root)

            claude_plan = plan_info.get("detected_plan", "pro")
            max_tokens = plan_info.get("token_limit", 200000)

            # Use actual context size
            estimated_context = current_context if current_context > 0 else 10
            usage_percent = (estimated_context / max_tokens) * 100

            # Get turn information
            turn_summary = self.turn_tracker.get_turn_summary()

            return {
                "usage_percent": min(usage_percent, 99.9),
                "tokens_used": estimated_context,
                "detected_plan": claude_plan,
                "max_tokens": max_tokens,
                "turn_number": turn_summary.get("current_turn", 0),
                "turn_tokens": turn_summary.get("current_turn_tokens", 0),
                "turn_display": self.turn_tracker.format_turn_display(),
            }

        except Exception:
            return {"usage_percent": 0, "tokens_used": 0}


class EnhancedStatus(BaseStatus):
    """Enhanced status line with multiple display modes"""

    def get_git_info(self):
        """Get current git branch and status"""
        try:
            # Determine the correct working directory
            git_cwd = self.project_root

            # Fallback: if PROJECT_ROOT doesn't have .git, use current working directory
            if not (git_cwd / ".git").exists() and (Path.cwd() / ".git").exists():
                git_cwd = Path.cwd()

            # Get current branch with multiple fallback methods
            branch = "unknown"
            for cmd in [
                ["git", "branch", "--show-current"],
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            ]:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=git_cwd,
                        timeout=2,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        branch = result.stdout.strip()
                        break
                except (subprocess.TimeoutExpired, OSError):
                    continue

            # Get status
            dirty = False
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=git_cwd,
                    timeout=2,
                )
                dirty = (
                    len(result.stdout.strip()) > 0 if result.returncode == 0 else False
                )
            except (subprocess.TimeoutExpired, OSError):
                pass

            return {"branch": branch, "dirty": dirty}
        except Exception:
            return {"branch": "unknown", "dirty": False}

    @staticmethod
    def format_tokens(count):
        """Format token count with K/M suffix"""
        if count >= 1000000:
            return f"{count / 1000000:.1f}M"
        elif count >= 1000:
            return f"{count / 1000:.0f}K"
        else:
            return str(count)

    def get_adaptive_threshold_info(self):
        """Get adaptive threshold information"""
        try:
            from .plan_detector import PlanDetector

            detector = PlanDetector(self.project_root)
            adaptive_threshold = detector.get_adaptive_threshold()
            default_threshold = float(os.environ.get("CONTEXT_THRESHOLD", 90))

            if abs(adaptive_threshold - default_threshold) > 1.0:
                return adaptive_threshold
            return None
        except:
            return None

    def format_compact(self):
        """Compact status line format"""
        usage = self.get_context_usage()
        git = self.get_git_info()

        usage_pct = usage["usage_percent"]
        current_dir = os.path.basename(os.getcwd())

        # Status indicators
        if usage_pct >= 90:
            ctx_icon = "🔴"
        elif usage_pct >= 75:
            ctx_icon = "🟡"
        elif usage_pct >= 50:
            ctx_icon = "🟢"
        else:
            ctx_icon = "🔵"

        # Git status
        git_symbol = "🌿±" if git["dirty"] else "🌿"
        detected_plan = usage.get("detected_plan", "pro")
        plan_symbol = "🎯" + detected_plan[0].upper()

        # Turn info
        turn_display = usage.get("turn_display", "")

        return f"📁{current_dir} │ {ctx_icon}{usage_pct:.0f}% │ {turn_display} │ {git_symbol}{git['branch']} │ {plan_symbol}"

    def format_detailed(self):
        """Detailed status line format"""
        usage = self.get_context_usage()
        git = self.get_git_info()

        usage_pct = usage["usage_percent"]
        tokens_used = usage["tokens_used"]

        # Get plan info
        plan = usage.get("detected_plan", "pro").upper()

        # Get current directory and username
        current_dir = os.path.basename(os.getcwd())
        username = os.environ.get("USER", "user")

        # Context status with color-coding
        if usage_pct >= 90:
            ctx_status = f"🔴 {usage_pct:.1f}%"
        elif usage_pct >= 75:
            ctx_status = f"🟡 {usage_pct:.1f}%"
        elif usage_pct >= 50:
            ctx_status = f"🟢 {usage_pct:.1f}%"
        else:
            ctx_status = f"🔵 {usage_pct:.1f}%"

        # Git status
        if git["dirty"]:
            git_status = f"🌿{git['branch']} ±"
        else:
            git_status = f"🌿{git['branch']}"

        # Add adaptive threshold indicator
        threshold_indicator = ""
        adaptive_threshold = self.get_adaptive_threshold_info()
        if adaptive_threshold:
            threshold_indicator = f" (→{adaptive_threshold:.0f}%)"

        # Turn info with formatted display
        turn_display = usage.get("turn_display", "")
        if turn_display:
            turn_info = f" │ 🔄 {turn_display}"
        else:
            turn_info = ""

        # Format output
        return f"💻 {username}:{current_dir} │ {ctx_status} ({self.format_tokens(tokens_used)}) │ {git_status} │ 🎯{plan}{threshold_indicator}{turn_info}"

    def get_status_json(self):
        """Get status as JSON"""
        usage = self.get_context_usage()
        git = self.get_git_info()
        adaptive_threshold = self.get_adaptive_threshold_info()

        data = {
            **usage,
            **git,
            "plan": usage.get("detected_plan", "pro"),
            "adaptive_threshold": adaptive_threshold,
        }
        return data


class StatusMonitor(BaseStatus):
    """Real-time status line monitor"""

    def format_status(self):
        """Format status line output"""
        usage = self.get_context_usage()

        usage_pct = usage["usage_percent"]
        tokens_used = usage["tokens_used"]
        max_tokens = usage["max_tokens"]

        # Color coding for usage levels
        if usage_pct >= 90:
            status_icon = "🔴"
            urgency = "CRITICAL"
        elif usage_pct >= 75:
            status_icon = "🟡"
            urgency = "HIGH"
        elif usage_pct >= 50:
            status_icon = "🟢"
            urgency = "OK"
        else:
            status_icon = "🔵"
            urgency = "LOW"

        tokens_display = (
            f"{self.format_tokens(tokens_used)}/{self.format_tokens(max_tokens)}"
        )

        # Status line format
        plan = os.environ.get("CLAUDE_PLAN", "pro").upper()

        # Add turn info
        turn_display = usage.get("turn_display", "")
        if turn_display:
            turn_info = f" | {turn_display}"
        else:
            turn_info = ""

        return f"{status_icon} {usage_pct:.1f}% ({tokens_display}) [{plan}] {urgency}{turn_info}"

    @staticmethod
    def format_tokens(count):
        """Format token count with K/M suffix"""
        if count >= 1000000:
            return f"{count / 1000000:.1f}M"
        elif count >= 1000:
            return f"{count / 1000:.0f}K"
        else:
            return str(count)
