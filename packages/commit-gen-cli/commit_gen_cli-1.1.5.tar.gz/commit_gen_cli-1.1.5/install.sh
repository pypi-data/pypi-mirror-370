#!/bin/bash

# Installation script for Commit-Gen

echo "Installing Commit-Gen - AI-Powered Git Commit Message Generator..."

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/commit-gen.py"
INSTALL_PATH="/usr/local/bin/commit-gen"

# Make sure the script is executable
chmod +x "$SCRIPT_PATH"

# Create symbolic link to make it globally available
if [ -L "$INSTALL_PATH" ]; then
    echo "Removing existing symlink..."
    sudo rm "$INSTALL_PATH"
fi

echo "Creating symlink at $INSTALL_PATH..."
sudo ln -s "$SCRIPT_PATH" "$INSTALL_PATH"

echo "Installation completed!"
echo "You can now use 'commit-gen' from anywhere in your terminal."
echo ""
echo "Setup your OpenRouter API key with:"
echo "commit-gen --api-key YOUR_API_KEY"
echo ""
echo "Or use Ollama locally with:"
echo "commit-gen --use-ollama"
