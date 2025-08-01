#!/bin/bash
# Install Claude Agent for GitHub Actions Improvement

set -e

echo "🤖 Installing Claude GitHub Actions Agent..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default installation directory
INSTALL_DIR="$HOME/.claude/agents/github-actions"

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy agent files
echo "📋 Copying agent files..."
cp "$SCRIPT_DIR/claude-agent-github-actions.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/claude-github-actions-agent.json" "$INSTALL_DIR/"

# Make executable
chmod +x "$INSTALL_DIR/claude-agent-github-actions.py"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "📝 Adding to PATH..."
    
    # Determine shell config file
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_CONFIG="$HOME/.bashrc"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    # Add to shell config
    echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_CONFIG"
    echo "Added to $SHELL_CONFIG"
fi

# Create symbolic link for easy access
ln -sf "$INSTALL_DIR/claude-agent-github-actions.py" "$INSTALL_DIR/github-actions-agent"

echo "✅ Installation complete!"
echo ""
echo "Usage from any repository:"
echo "  # Direct usage"
echo "  $INSTALL_DIR/claude-agent-github-actions.py"
echo "  "
echo "  # Or if PATH was updated (restart shell first):"
echo "  github-actions-agent"
echo ""
echo "Usage from Claude CLI:"
echo "  claude --prompt 'Improve GitHub Actions in this repository'"
echo "  claude --prompt 'Create GitHub Actions workflows for this project'"
echo "  claude --prompt 'Fix failing GitHub Actions workflows'"
echo ""
echo "Features:"
echo "  ✅ Concurrent processing of multiple workflows"
echo "  ✅ Project type detection (Python, Node.js, Rust, Go, Java, etc.)"
echo "  ✅ Creates CI, security, and release workflows"
echo "  ✅ Improves existing workflows with best practices"
echo "  ✅ Fixes common workflow issues"
echo ""
echo "🎉 Ready to use! Try it in any Git repository."