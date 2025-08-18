#!/usr/bin/env python3
"""
Installer for Claude Context Monitor
"""

import shutil
import subprocess
from pathlib import Path


class Installer:
    """Handles installation and uninstallation of Claude Context Monitor"""

    def __init__(self):
        """Initialize installer"""
        self.claude_dir = Path.home() / ".claude"
        self.commands_dir = self.claude_dir / "commands"
        self.package_dir = Path(__file__).parent
        self.config_template = self.package_dir / "config" / "config.sh"

    def install(self, force=False, global_cmd=True, verbose=False):
        """Install Claude Context Monitor"""
        try:
            if verbose:
                print("🚀 Installing Claude Context Monitor...")

            # Create directories
            self.claude_dir.mkdir(exist_ok=True)
            self.commands_dir.mkdir(exist_ok=True)

            # Install Python package files
            self._install_python_files(force, verbose)

            # Install configuration
            self._install_config(force, verbose)

            # Install shell scripts
            self._install_shell_scripts(force, verbose)

            # Install command definitions
            self._install_commands(force, verbose)

            # Install global commands
            if global_cmd:
                self._install_global_commands(verbose)

            # Configure global status integration
            self._configure_global_status(verbose)

            if verbose:
                print("✅ Installation completed successfully!")

            return True

        except Exception as e:
            if verbose:
                print(f"❌ Installation failed: {e}")
            return False

    def _install_python_files(self, force, verbose):
        """Install Python module files"""
        files_to_install = [
            ("status.py", "enhanced-status.py"),
            ("status.py", "status-monitor.py"),  # Legacy compatibility
            ("plan_detector.py", "intelligent_plan_detector.py"),
            ("handoff.py", "handoff_tracker.py"),  # Legacy compatibility
        ]

        for src_name, dst_name in files_to_install:
            src_file = self.package_dir / src_name
            dst_file = self.claude_dir / dst_name

            if dst_file.exists() and not force:
                if verbose:
                    print(f"📝 {dst_name} exists, skipping")
                continue

            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                dst_file.chmod(0o755)  # Make executable
                if verbose:
                    print(f"📦 Installed {dst_name}")

    def _install_config(self, force, verbose):
        """Install configuration files"""
        config_file = self.claude_dir / "config.sh"

        if not config_file.exists():
            if self.config_template.exists():
                shutil.copy2(self.config_template, config_file)
                if verbose:
                    print("⚙️ Installed configuration")
            else:
                # Create default config
                default_config = """#!/bin/bash
# Claude Code Context Monitor Configuration

# Set your Claude plan (pro, max, max5, max20, custom)
export CLAUDE_PLAN="max"

# Context warning threshold (percentage)
export CONTEXT_THRESHOLD=90

# Status line refresh interval (milliseconds)
export STATUS_REFRESH_INTERVAL=3000

# Configuration loaded silently
"""
                config_file.write_text(default_config)
                if verbose:
                    print("⚙️ Created default configuration")
        elif verbose:
            print("📝 Configuration exists, keeping current settings")

    def _install_shell_scripts(self, force, verbose):
        """Install shell scripts"""
        scripts_dir = self.package_dir / "scripts"
        if not scripts_dir.exists():
            return

        for script_file in scripts_dir.glob("*.sh"):
            dst_file = self.claude_dir / script_file.name

            if dst_file.exists() and not force:
                continue

            shutil.copy2(script_file, dst_file)
            dst_file.chmod(0o755)
            if verbose:
                print(f"🔧 Installed {script_file.name}")

    def _install_commands(self, force, verbose):
        """Install Claude Code command definitions"""
        commands_src = self.package_dir / "commands"
        if not commands_src.exists():
            return

        for cmd_file in commands_src.glob("*.md"):
            dst_file = self.commands_dir / cmd_file.name

            if dst_file.exists() and not force:
                continue

            shutil.copy2(cmd_file, dst_file)
            if verbose:
                print(f"📋 Installed /{cmd_file.stem} command")

    def _install_global_commands(self, verbose):
        """Install global command line tools"""
        try:
            # Check if we can install globally
            if shutil.which("pip"):
                # Try to install as editable package
                result = subprocess.run(
                    ["pip", "install", "-e", str(self.package_dir.parent)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    if verbose:
                        print("🛠️ Installed global commands: claude-context, ccm")
                    return True

            if verbose:
                print("⚠️ Could not install global commands (pip not available)")
            return False

        except Exception as e:
            if verbose:
                print(f"⚠️ Could not install global commands: {e}")
            return False

    def _configure_global_status(self, verbose):
        """Configure global status line integration"""
        try:
            # This would integrate with shell configuration
            # For now, just ensure the scripts are in place
            if verbose:
                print("🎨 Global status integration available")
        except Exception as e:
            if verbose:
                print(f"⚠️ Could not configure global status: {e}")

    def uninstall(self, verbose=False):
        """Uninstall Claude Context Monitor"""
        try:
            if verbose:
                print("🗑️ Uninstalling Claude Context Monitor...")

            # Remove installed files
            files_to_remove = [
                "enhanced-status.py",
                "status-monitor.py",
                "intelligent_plan_detector.py",
                "handoff_tracker.py",
                "config.sh",
            ]

            for filename in files_to_remove:
                file_path = self.claude_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    if verbose:
                        print(f"🗑️ Removed {filename}")

            # Remove commands
            cmd_files = [
                "handoff.md",
            ]

            for cmd_file in cmd_files:
                cmd_path = self.commands_dir / cmd_file
                if cmd_path.exists():
                    cmd_path.unlink()
                    if verbose:
                        print(f"🗑️ Removed /{cmd_file.replace('.md', '')} command")

            # Try to uninstall global commands
            try:
                result = subprocess.run(
                    ["pip", "uninstall", "claude-context-monitor", "-y"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and verbose:
                    print("🗑️ Removed global commands")
            except Exception:
                pass

            if verbose:
                print("✅ Uninstallation completed!")

            return True

        except Exception as e:
            if verbose:
                print(f"❌ Uninstallation failed: {e}")
            return False
