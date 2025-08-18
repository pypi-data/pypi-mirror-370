"""Real-time monitoring with animated token display."""

import time
import sys
from threading import Event

from .status import EnhancedStatus


class RealtimeMonitor:
    """Real-time context monitor with animated token display."""

    def __init__(self, format_mode="detailed", update_interval=0.05):
        """Initialize the real-time monitor.

        Args:
            format_mode: Display format (detailed, compact, minimal)
            update_interval: Update interval in seconds
        """
        self.status = EnhancedStatus()
        self.format_mode = format_mode
        self.update_interval = update_interval
        self.stop_event = Event()
        self.last_update_time = 0
        self.last_status_check = 0
        self.status_check_interval = 2.0  # Check for new data every 2 seconds

    def clear_line(self):
        """Clear the current terminal line."""
        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

    def format_output(self, usage_data):
        """Format the status output with animated values.

        Args:
            usage_data: Context usage data dictionary

        Returns:
            Formatted string for display
        """
        if self.format_mode == "compact":
            return self.status.format_compact()
        elif self.format_mode == "minimal":
            # Minimal format with just percentage and turn info
            usage_pct = usage_data.get("usage_percent", 0)
            turn_display = usage_data.get("turn_display", "")

            # Color coding
            if usage_pct >= 90:
                icon = "🔴"
            elif usage_pct >= 75:
                icon = "🟡"
            elif usage_pct >= 50:
                icon = "🟢"
            else:
                icon = "🔵"

            return f"{icon} {usage_pct:.1f}% │ {turn_display}"
        else:
            return self.status.format_detailed()

    def run(self):
        """Run the real-time monitoring loop."""
        print("🚀 Starting real-time context monitor (Ctrl+C to stop)")
        print()

        try:
            while not self.stop_event.is_set():
                current_time = time.time()

                # Check for new status data periodically
                if current_time - self.last_status_check >= self.status_check_interval:
                    # Get fresh context data
                    usage_data = self.status.get_context_usage()
                    self.last_status_check = current_time

                    # Force a display update
                    self.last_update_time = 0

                # Update display at animation frame rate
                if current_time - self.last_update_time >= self.update_interval:
                    # Get current context usage
                    usage_data = self.status.get_context_usage()

                    # Format with current animated values
                    output = self.format_output(usage_data)

                    # Clear line and write new status
                    self.clear_line()
                    sys.stdout.write(f"\r{output}")
                    sys.stdout.flush()

                    self.last_update_time = current_time

                # Small sleep to control CPU usage
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            print("\n\n✋ Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            # Final status display
            usage_data = self.status.get_context_usage()
            output = self.format_output(usage_data)
            self.clear_line()
            print(f"{output}")
            print()

    def stop(self):
        """Stop the monitoring loop."""
        self.stop_event.set()


def watch_context(format_mode="detailed", interval=0.05):
    """Convenience function to start real-time monitoring.

    Args:
        format_mode: Display format
        interval: Update interval in seconds
    """
    monitor = RealtimeMonitor(format_mode=format_mode, update_interval=interval)
    monitor.run()
