#!/usr/bin/env python3
"""
Uninstall script for Commit-Gen.
This script cleans up all configuration files and symlinks created by the package.
"""

import os
import shutil
from pathlib import Path


def cleanup_config_files():
    """Remove all configuration files created by commit-gen."""
    config_dir = Path.home() / ".config" / "git-commit-ai"
    if config_dir.exists():
        try:
            shutil.rmtree(config_dir)
            print(f"✅ Removed configuration directory: {config_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove config directory: {e}")


def cleanup_symlink():
    """Remove symlink created by install.sh."""
    symlink_path = Path("/usr/local/bin/commit-gen")
    if symlink_path.exists() and symlink_path.is_symlink():
        try:
            # Check if it's our symlink
            target = symlink_path.resolve()
            if "gen-commit-message" in str(target):
                os.unlink(symlink_path)
                print(f"✅ Removed symlink: {symlink_path}")
            else:
                print(f"⚠️  Warning: Symlink {symlink_path} points to {target}, not removing")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove symlink: {e}")


def main():
    """Main uninstall function."""
    print("🧹 Cleaning up Commit-Gen installation...")

    cleanup_config_files()
    cleanup_symlink()

    print("✅ Cleanup completed!")
    print("\n📝 Note: If you installed commit-gen via pip, also run:")
    print("   pip uninstall commit-gen")


if __name__ == "__main__":
    main()
