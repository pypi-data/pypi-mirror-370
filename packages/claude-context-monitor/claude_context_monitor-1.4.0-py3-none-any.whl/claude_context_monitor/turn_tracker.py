"""Turn-by-turn token tracking for Claude Context Monitor."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from .token_animator import animate_tokens, get_animated_value, reset_animation


@dataclass
class Turn:
    """Represents a single conversation turn."""

    turn_number: int
    timestamp: str
    input_tokens: int
    output_tokens: int
    cache_read: int
    cache_create: int
    total_tokens: int
    cumulative_tokens: int

    @property
    def turn_tokens(self) -> int:
        """Tokens used in this turn only."""
        return self.total_tokens


class TurnTracker:
    """Tracks token usage per conversation turn."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the turn tracker.

        Args:
            cache_dir: Directory to store turn history. Defaults to ~/.claude_context_monitor/
        """
        self.cache_dir = cache_dir or Path.home() / ".claude_context_monitor"
        self.cache_dir.mkdir(exist_ok=True)
        self.turn_file = self.cache_dir / "turn_history.json"

        self.turns: List[Turn] = []
        self.current_turn = 0
        self.last_update: Optional[datetime] = None
        self.previous_total = 0

        # Turn detection threshold (seconds between turns)
        self.turn_threshold = 60  # New turn after 1 minute gap

        self._load_history()

    def _load_history(self) -> None:
        """Load turn history from cache file."""
        if self.turn_file.exists():
            try:
                with open(self.turn_file, "r") as f:
                    data = json.load(f)
                    # Check if this is today's data
                    if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                        self.turns = [Turn(**turn) for turn in data.get("turns", [])]
                        self.current_turn = data.get("current_turn", 0)
                        self.previous_total = data.get("previous_total", 0)
            except (json.JSONDecodeError, KeyError):
                # Reset on error
                self.turns = []

    def _save_history(self) -> None:
        """Save turn history to cache file."""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "turns": [asdict(turn) for turn in self.turns],
            "current_turn": self.current_turn,
            "previous_total": self.previous_total,
        }
        with open(self.turn_file, "w") as f:
            json.dump(data, f, indent=2)

    def update(
        self,
        timestamp: datetime,
        input_tokens: int,
        output_tokens: int,
        cache_read: int,
        cache_create: int,
        total_cumulative: int,
    ) -> Tuple[int, int]:
        """Update turn tracking with new token data.

        Args:
            timestamp: Current timestamp
            input_tokens: Input tokens for this update
            output_tokens: Output tokens for this update
            cache_read: Cache read tokens
            cache_create: Cache creation tokens
            total_cumulative: Total cumulative tokens so far

        Returns:
            Tuple of (current_turn_tokens, turn_number)
        """
        # First call - initialize
        if not self.turns:
            self.current_turn = 1
            self.previous_total = 0
            turn_tokens = max(0, total_cumulative)

            turn = Turn(
                turn_number=self.current_turn,
                timestamp=timestamp.isoformat(),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_read=cache_read,
                cache_create=cache_create,
                total_tokens=turn_tokens,
                cumulative_tokens=total_cumulative,
            )

            self.turns.append(turn)
            self.previous_total = total_cumulative
            self._save_history()

            # Start animation for first turn
            animation_key = f"turn_{self.current_turn}"
            reset_animation(animation_key)
            animate_tokens(animation_key, turn_tokens)

            return turn_tokens, self.current_turn

        # Update existing turn
        last_turn = self.turns[-1]
        turn_tokens = max(0, total_cumulative)  # Use total as current turn tokens

        # Only update if tokens have increased significantly
        if turn_tokens > last_turn.total_tokens:
            last_turn.total_tokens = turn_tokens
            last_turn.cumulative_tokens = total_cumulative
            last_turn.output_tokens = output_tokens
            self._save_history()

            # Update animation for current turn
            animation_key = f"turn_{self.current_turn}"
            animate_tokens(animation_key, turn_tokens)

        return last_turn.total_tokens, self.current_turn

    def _detect_new_turn(self, timestamp: datetime, total_tokens: int) -> bool:
        """Detect if this update represents a new conversation turn.

        Args:
            timestamp: Current timestamp
            total_tokens: Current total tokens

        Returns:
            True if this is a new turn
        """
        # First update is always a new turn
        if self.last_update is None or not self.turns:
            self.last_update = timestamp
            # Only create turn if there are actual tokens
            return total_tokens > 0

        # Check time gap
        time_gap = (timestamp - self.last_update).total_seconds()

        # Token increase from last known total
        token_increase = total_tokens - self.previous_total

        # New turn if:
        # 1. Significant time has passed (> threshold) AND there's a token increase
        # 2. OR massive token jump (> 2000 tokens in one go - indicates new conversation)
        is_new = (
            time_gap > self.turn_threshold and token_increase > 100
        ) or token_increase > 2000

        self.last_update = timestamp
        return is_new

    def get_current_turn_tokens(self) -> int:
        """Get token count for the current turn."""
        if self.turns:
            return self.turns[-1].total_tokens
        return 0

    def get_turn_summary(self) -> Dict:
        """Get summary statistics for all turns."""
        if not self.turns:
            return {
                "total_turns": 0,
                "average_tokens_per_turn": 0,
                "max_turn_tokens": 0,
                "min_turn_tokens": 0,
                "current_turn": 0,
                "current_turn_tokens": 0,
            }

        turn_tokens = [t.total_tokens for t in self.turns]
        return {
            "total_turns": len(self.turns),
            "average_tokens_per_turn": sum(turn_tokens) // len(turn_tokens),
            "max_turn_tokens": max(turn_tokens),
            "min_turn_tokens": min(turn_tokens),
            "current_turn": self.current_turn,
            "current_turn_tokens": self.get_current_turn_tokens(),
        }

    def format_turn_display(self, animated: bool = True) -> str:
        """Format turn information for display.

        Args:
            animated: Whether to use animated token values

        Returns:
            Formatted string like "Turn 3: 1.2k↑"
        """
        if not self.turns:
            return "Turn 1: 0"

        if animated:
            # Use animated value with growth indicator
            animation_key = f"turn_{self.current_turn}"
            token_str = get_animated_value(
                animation_key, formatted=True, show_growth=True
            )
        else:
            # Use static value
            current_tokens = self.get_current_turn_tokens()
            if current_tokens >= 1000:
                token_str = f"{current_tokens / 1000:.1f}k"
            else:
                token_str = str(current_tokens)

        return f"Turn {self.current_turn}: {token_str}"

    def reset(self) -> None:
        """Reset turn tracking for a new session."""
        self.turns = []
        self.current_turn = 0
        self.last_update = None
        self.previous_total = 0
        if self.turn_file.exists():
            self.turn_file.unlink()
