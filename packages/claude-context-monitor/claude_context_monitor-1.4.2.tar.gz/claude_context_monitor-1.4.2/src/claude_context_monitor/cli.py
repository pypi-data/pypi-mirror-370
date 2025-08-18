#!/usr/bin/env python3
"""
Claude Context Monitor CLI
Unified command-line interface for all monitoring features
"""

import argparse
import json
import sys
import os
from pathlib import Path

from .status import EnhancedStatus, StatusMonitor
from .plan_detector import detect_claude_plan
from .handoff import HandoffTracker
from .installer import Installer
from .realtime_monitor import RealtimeMonitor


def cmd_status(args):
    """Display current context status"""
    status = EnhancedStatus()

    if args.format == "json":
        result = status.get_status_json()
        print(json.dumps(result, indent=2))
    elif args.format == "compact":
        print(status.format_compact())
    else:  # detailed
        print(status.format_detailed())


def cmd_monitor(args):
    """Run continuous monitoring"""
    monitor = StatusMonitor()

    if args.json:
        result = monitor.get_context_usage()
        print(json.dumps(result, indent=2))
    else:
        print(monitor.format_status())


def cmd_watch(args):
    """Run real-time monitoring with animated display"""
    monitor = RealtimeMonitor(format_mode=args.format, update_interval=args.interval)
    monitor.run()


def cmd_handoff(args):
    """Record handoff and manage adaptive thresholds"""
    tracker = HandoffTracker()

    if args.record:
        result = tracker.record_handoff()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(
                    f"🎯 Handoff recorded at {result['context_percentage']}% context usage"
                )
                print(
                    f"📊 Tokens: {result['total_tokens']:,} / {result['max_tokens']:,}"
                )
                print(f"🔧 Adaptive threshold: {result['adaptive_threshold']}%")
                if result["handoff_count"] > 1:
                    print(
                        f"📈 Historical average: {result.get('avg_handoff_percentage', 0):.1f}% ({result['handoff_count']} handoffs)"
                    )
            else:
                print(f"❌ Failed to record handoff: {result.get('error')}")

    elif args.summary:
        print(tracker.get_handoff_summary())

    elif args.stats:
        stats = tracker.get_handoff_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("📊 Handoff Statistics")
            print(f"  Count: {stats['handoff_count']}")
            if stats["avg_handoff_percentage"]:
                print(f"  Average: {stats['avg_handoff_percentage']:.1f}%")
                print(f"  Min: {stats['min_handoff_percentage']:.1f}%")
                print(f"  Max: {stats['max_handoff_percentage']:.1f}%")
            print(f"  Adaptive Threshold: {stats['adaptive_threshold']:.1f}%")
            if stats["last_handoff"]:
                print(f"  Last Handoff: {stats['last_handoff']}")


def cmd_plan(args):
    """Detect Claude plan and analyze usage"""
    result = detect_claude_plan()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("🎯 Claude Plan Detection")
        print(f"  Detected Plan: {result['detected_plan'].upper()}")
        print(f"  Confidence: {result['confidence'] * 100:.1f}%")
        print(f"  Token Limit: {result['token_limit']:,}")
        print(f"  Method: {result['method']}")

        if result.get("p90_limit"):
            print(f"  P90 Limit: {result['p90_limit']:,}")

        if result.get("sessions_analyzed"):
            print(f"  Sessions Analyzed: {result['sessions_analyzed']}")

        if result.get("handoff_stats"):
            stats = result["handoff_stats"]
            if stats["handoff_count"] > 0:
                print("\n📈 Adaptive Learning")
                print(f"  Handoffs Recorded: {stats['handoff_count']}")
                print(f"  Adaptive Threshold: {result['adaptive_threshold']:.1f}%")


def cmd_install(args):
    """Install or update Claude Context Monitor"""
    installer = Installer()

    success = installer.install(
        force=args.force, global_cmd=not args.no_global, verbose=args.verbose
    )
    if success:
        print("✅ Claude Context Monitor installed successfully")
        print("\nUsage:")
        print("  claude-context status      # Show current status")
        print("  claude-context handoff     # Record handoff")
        print("  ccm status -f detailed    # Use short alias")
    else:
        print("❌ Installation failed")
        sys.exit(1)


def cmd_uninstall(args):
    """Uninstall Claude Context Monitor"""
    installer = Installer()

    success = installer.uninstall()
    if success:
        print("✅ Claude Context Monitor uninstalled successfully")
    else:
        print("❌ Failed to uninstall")
        sys.exit(1)


def cmd_config(args):
    """Manage configuration"""
    config_file = Path.home() / ".claude" / "config.sh"

    if args.show:
        if config_file.exists():
            with open(config_file, "r") as f:
                print(f.read())
        else:
            print("No configuration file found")

    elif args.set:
        key, value = args.set.split("=", 1)
        # Update config file
        lines = []
        updated = False

        if config_file.exists():
            with open(config_file, "r") as f:
                for line in f:
                    if line.startswith(f"export {key}="):
                        lines.append(f'export {key}="{value}"\n')
                        updated = True
                    else:
                        lines.append(line)

        if not updated:
            lines.append(f'export {key}="{value}"\n')

        with open(config_file, "w") as f:
            f.writelines(lines)

        print(f"✅ Set {key}={value}")

    elif args.get:
        value = os.environ.get(args.get, "")
        if value:
            print(f"{args.get}={value}")
        else:
            print(f"{args.get} is not set")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="claude-context",
        description="Claude Context Monitor - Advanced context monitoring for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show current context status
  %(prog)s status -f detailed        # Detailed status view
  %(prog)s status -f json           # JSON output
  
  %(prog)s handoff --record         # Record handoff for learning
  %(prog)s handoff --stats          # Show handoff statistics
  
  %(prog)s plan                     # Detect Claude plan
  %(prog)s plan --json              # Plan detection as JSON
  
  %(prog)s config --show            # Show configuration
  %(prog)s config --set CLAUDE_PLAN=max  # Set config value
  
  %(prog)s install                  # Install to ~/.claude
  %(prog)s install --force          # Force reinstall
  %(prog)s uninstall                # Uninstall from ~/.claude

Short alias 'claude-ctx' is also available for all commands.
        """,
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.4.2")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Display current context status"
    )
    status_parser.add_argument(
        "-f",
        "--format",
        choices=["detailed", "compact", "json"],
        default="detailed",
        help="Output format (default: detailed)",
    )

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Run context monitoring")
    monitor_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Watch command (real-time monitoring with animation)
    watch_parser = subparsers.add_parser(
        "watch", help="Real-time monitoring with animated token display"
    )
    watch_parser.add_argument(
        "-f",
        "--format",
        choices=["detailed", "compact", "minimal"],
        default="detailed",
        help="Display format (default: detailed)",
    )
    watch_parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=0.05,
        help="Update interval in seconds (default: 0.05)",
    )

    # Handoff command
    handoff_parser = subparsers.add_parser(
        "handoff", help="Manage handoffs and adaptive thresholds"
    )
    handoff_group = handoff_parser.add_mutually_exclusive_group()
    handoff_group.add_argument(
        "--record", action="store_true", help="Record current context as handoff"
    )
    handoff_group.add_argument(
        "--summary", action="store_true", help="Get handoff summary for documents"
    )
    handoff_group.add_argument(
        "--stats", action="store_true", help="Show handoff statistics"
    )
    handoff_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Plan detection command
    plan_parser = subparsers.add_parser(
        "plan", help="Detect Claude plan and analyze usage"
    )
    plan_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Install command
    install_parser = subparsers.add_parser(
        "install", help="Install or update Claude Context Monitor"
    )
    install_parser.add_argument(
        "--force", action="store_true", help="Force reinstall even if already installed"
    )
    install_parser.add_argument(
        "--no-global", action="store_true", help="Skip global command installation"
    )
    install_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Uninstall command
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Uninstall Claude Context Monitor"
    )
    uninstall_parser.add_argument(
        "--verbose", action="store_true", help="Verbose output"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )
    config_group.add_argument(
        "--set", metavar="KEY=VALUE", help="Set configuration value"
    )
    config_group.add_argument("--get", metavar="KEY", help="Get configuration value")

    args = parser.parse_args()

    if not args.command:
        # Default to status command
        args.command = "status"
        args.format = "detailed"

    # Route to appropriate command
    commands = {
        "status": cmd_status,
        "monitor": cmd_monitor,
        "watch": cmd_watch,
        "handoff": cmd_handoff,
        "plan": cmd_plan,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
        "config": cmd_config,
    }

    if args.command in commands:
        try:
            commands[args.command](args)
        except KeyboardInterrupt:
            print("\n✋ Interrupted")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
