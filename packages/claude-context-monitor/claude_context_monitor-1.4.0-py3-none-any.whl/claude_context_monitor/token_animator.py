"""Animated token counter for smooth transitions."""

import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class AnimationState:
    """State for a single animation."""

    start_value: int
    target_value: int
    current_value: float
    start_time: float
    duration: float = 1.5  # Animation duration in seconds

    def is_complete(self) -> bool:
        """Check if animation is complete."""
        return time.time() - self.start_time >= self.duration

    def get_progress(self) -> float:
        """Get animation progress (0.0 to 1.0)."""
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / self.duration)


class TokenAnimator:
    """Manages smooth token count animations."""

    def __init__(self):
        """Initialize the animator."""
        self.animations = {}  # track animations by key
        self.lock = threading.Lock()
        self.update_thread = None
        self.running = False
        self.callback: Optional[Callable] = None

    def animate(
        self, key: str, target_value: int, callback: Optional[Callable] = None
    ) -> None:
        """Start animating a value from current to target.

        Args:
            key: Unique identifier for this animation
            target_value: Target token count
            callback: Optional callback for updates
        """
        with self.lock:
            # Get current value if animation exists
            if key in self.animations:
                current = int(self.animations[key].current_value)
            else:
                current = 0

            # Only animate if value changed
            if current == target_value:
                return

            # Create new animation state
            self.animations[key] = AnimationState(
                start_value=current,
                target_value=target_value,
                current_value=float(current),
                start_time=time.time(),
            )

            if callback:
                self.callback = callback

            # Start update thread if not running
            if not self.running:
                self.running = True
                self.update_thread = threading.Thread(
                    target=self._update_loop, daemon=True
                )
                self.update_thread.start()

    def _update_loop(self) -> None:
        """Background thread to update animations."""
        while self.running:
            with self.lock:
                # Update all animations
                completed = []
                any_active = False

                for key, state in self.animations.items():
                    if state.is_complete():
                        state.current_value = float(state.target_value)
                        completed.append(key)
                    else:
                        # Apply easing function for smooth animation
                        progress = state.get_progress()
                        eased_progress = self._ease_out_cubic(progress)

                        # Calculate current value
                        diff = state.target_value - state.start_value
                        state.current_value = state.start_value + (
                            diff * eased_progress
                        )
                        any_active = True

                # Clean up completed animations after a delay
                for key in completed:
                    anim = self.animations[key]
                    if time.time() - anim.start_time > anim.duration + 1.0:
                        del self.animations[key]

                # Stop thread if no active animations
                if not any_active and not self.animations:
                    self.running = False

                # Trigger callback if set
                if self.callback:
                    self.callback()

            # Small sleep to control update rate (60 FPS)
            time.sleep(0.016)

    def _ease_out_cubic(self, t: float) -> float:
        """Cubic easing out function for smooth deceleration.

        Args:
            t: Progress value from 0.0 to 1.0

        Returns:
            Eased value from 0.0 to 1.0
        """
        return 1 - pow(1 - t, 3)

    def _ease_in_out_quad(self, t: float) -> float:
        """Quadratic easing in/out for smooth acceleration and deceleration.

        Args:
            t: Progress value from 0.0 to 1.0

        Returns:
            Eased value from 0.0 to 1.0
        """
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2

    def get_current_value(self, key: str) -> int:
        """Get current animated value for a key.

        Args:
            key: Animation key

        Returns:
            Current integer value
        """
        with self.lock:
            if key in self.animations:
                return int(self.animations[key].current_value)
            return 0

    def get_formatted_value(self, key: str, show_growth: bool = True) -> str:
        """Get formatted animated value with optional growth indicator.

        Args:
            key: Animation key
            show_growth: Whether to show upward arrow during animation

        Returns:
            Formatted string like "1.2k" or "1.2k↑"
        """
        with self.lock:
            if key not in self.animations:
                return "0"

            state = self.animations[key]
            current = int(state.current_value)

            # Format the number
            if current >= 1000:
                formatted = f"{current / 1000:.1f}k"
            else:
                formatted = str(current)

            # Add growth indicator if animating
            if show_growth and not state.is_complete():
                # Show different indicators based on speed
                diff = state.target_value - state.start_value
                if diff > 5000:
                    formatted += "⇈"  # Fast growth
                elif diff > 1000:
                    formatted += "↑"  # Normal growth
                else:
                    formatted += "↗"  # Slow growth

            return formatted

    def reset(self, key: str) -> None:
        """Reset animation for a key.

        Args:
            key: Animation key to reset
        """
        with self.lock:
            if key in self.animations:
                del self.animations[key]

    def reset_all(self) -> None:
        """Reset all animations."""
        with self.lock:
            self.animations.clear()
            self.running = False


# Global animator instance
_global_animator = TokenAnimator()


def animate_tokens(key: str, target: int, callback: Optional[Callable] = None) -> None:
    """Convenience function to animate token count.

    Args:
        key: Unique identifier for this animation
        target: Target token count
        callback: Optional callback for updates
    """
    _global_animator.animate(key, target, callback)


def get_animated_value(
    key: str, formatted: bool = True, show_growth: bool = True
) -> str:
    """Get current animated value.

    Args:
        key: Animation key
        formatted: Whether to format with k/M suffix
        show_growth: Whether to show growth indicator

    Returns:
        Current value as string
    """
    if formatted:
        return _global_animator.get_formatted_value(key, show_growth)
    return str(_global_animator.get_current_value(key))


def reset_animation(key: str) -> None:
    """Reset a specific animation."""
    _global_animator.reset(key)
