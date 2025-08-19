#!/bin/bash

# Uninstall script for Commit-Gen

echo "🧹 Uninstalling Commit-Gen - AI-Powered Git Commit Message Generator..."

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNINSTALL_PATH="/usr/local/bin/commit-gen"

# Remove symlink if it exists and points to our script
if [ -L "$UNINSTALL_PATH" ]; then
    TARGET=$(readlink "$UNINSTALL_PATH")
    if [[ "$TARGET" == *"gen-commit-message"* ]]; then
        echo "Removing symlink at $UNINSTALL_PATH..."
        sudo rm "$UNINSTALL_PATH"
        echo "✅ Symlink removed successfully"
    else
        echo "⚠️  Warning: Symlink points to $TARGET, not removing"
    fi
else
    echo "ℹ️  No symlink found at $UNINSTALL_PATH"
fi

# Remove configuration directory
CONFIG_DIR="$HOME/.config/git-commit-ai"
if [ -d "$CONFIG_DIR" ]; then
    echo "Removing configuration directory..."
    rm -rf "$CONFIG_DIR"
    echo "✅ Configuration directory removed successfully"
else
    echo "ℹ️  No configuration directory found"
fi

# Check if installed via pip
if command -v pip &> /dev/null; then
    if pip show commit-gen &> /dev/null; then
        echo ""
        echo "📦 Found commit-gen package installed via pip"
        echo "To completely uninstall, run:"
        echo "   pip uninstall commit-gen"
    fi
fi

echo ""
echo "✅ Uninstallation completed!"
echo ""
echo "📝 If you want to reinstall later:"
echo "   ./install.sh    # For manual installation"
echo "   pip install commit-gen  # For package installation" 