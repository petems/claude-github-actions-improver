#!/bin/bash
# Install Claude Slash Commands for GitHub Actions

set -e

echo "⚡ Installing Claude Slash Commands for GitHub Actions..."

# Get Claude config directory
CLAUDE_CONFIG_DIR="$HOME/.config/claude"
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/claude"
fi

# Create config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if settings.json exists
SETTINGS_FILE="$CLAUDE_CONFIG_DIR/settings.json"

if [[ -f "$SETTINGS_FILE" ]]; then
    echo "📋 Found existing Claude settings.json"
    
    # Backup existing settings
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📋 Backed up existing settings"
    
    # Check if slash commands already exist
    if grep -q '"slashCommands"' "$SETTINGS_FILE"; then
        echo "⚠️  Slash commands section already exists in settings.json"
        echo "Please manually merge the commands from:"
        echo "  $SCRIPT_DIR/claude-slash-commands.json"
        echo "Into your existing settings.json at:"
        echo "  $SETTINGS_FILE"
        echo ""
        echo "Or remove the existing slashCommands section and run this script again."
        exit 1
    else
        # Add slash commands to existing settings
        echo "➕ Adding slash commands to existing settings..."
        
        # Read the slash commands
        SLASH_COMMANDS=$(cat "$SCRIPT_DIR/claude-slash-commands.json")
        
        # Use jq to merge if available, otherwise manual merge
        if command -v jq >/dev/null 2>&1; then
            # Use jq for proper JSON merging
            jq --argjson slashCommands "$SLASH_COMMANDS" '.slashCommands = $slashCommands.commands' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
            mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        else
            # Manual merge (remove closing brace, add comma and slash commands)
            head -n -1 "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
            echo '  ,' >> "$SETTINGS_FILE.tmp"
            echo '  "slashCommands": {' >> "$SETTINGS_FILE.tmp"
            
            # Extract just the commands content
            sed -n '/"\/actions":/,/"\/ci":/p' "$SCRIPT_DIR/claude-slash-commands.json" | head -n -1 >> "$SETTINGS_FILE.tmp"
            
            echo '  }' >> "$SETTINGS_FILE.tmp"
            echo '}' >> "$SETTINGS_FILE.tmp"
            mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        fi
    fi
else
    echo "📋 Creating new Claude settings.json"
    
    # Create new settings file with slash commands
    cat > "$SETTINGS_FILE" << 'EOF'
{
  "slashCommands": {
    "/actions": {
      "description": "Improve GitHub Actions in this repository (full analysis)",
      "prompt": "Analyze this repository and improve the GitHub Actions workflows. Detect the project type, create workflows if none exist, improve existing workflows with best practices, and fix any common issues. Process multiple workflows concurrently for efficiency.",
      "working_directory_required": true,
      "git_repository_required": true
    },
    "/actions-create": {
      "description": "Create GitHub Actions workflows for this project",
      "prompt": "Analyze this project and create appropriate GitHub Actions workflows. Detect the project type (Python, Node.js, Rust, Go, Java, etc.) and create CI/CD pipelines, security scanning, and release workflows tailored to the project. Use modern best practices and latest action versions.",
      "working_directory_required": true,
      "git_repository_required": true
    },
    "/actions-fix": {
      "description": "Fix failing GitHub Actions workflows",
      "prompt": "Analyze all GitHub Actions workflows in this repository and fix common issues like outdated action versions, syntax errors, missing dependencies, permission problems, and caching issues. Process multiple workflows concurrently.",
      "working_directory_required": true,
      "git_repository_required": true
    },
    "/actions-improve": {
      "description": "Improve existing GitHub Actions with best practices",
      "prompt": "Improve all existing GitHub Actions workflows in this repository by updating to latest action versions with SHA pinning, adding security hardening, optimizing caching strategies, improving matrix configurations, and adding proper permissions. Process workflows concurrently.",
      "working_directory_required": true,
      "git_repository_required": true
    },
    "/actions-security": {
      "description": "Add security scanning to GitHub Actions",
      "prompt": "Analyze this project and add comprehensive security scanning to GitHub Actions workflows. Include dependency vulnerability scanning, SAST analysis, license compliance checking, and security best practices. Create or enhance security workflows.",
      "working_directory_required": true,
      "git_repository_required": true
    },
    "/ci": {
      "description": "Quick CI workflow creation", 
      "prompt": "Create a modern CI/CD workflow for this project. Detect the project type and create an optimized continuous integration pipeline with testing, linting, caching, and matrix builds where appropriate.",
      "working_directory_required": true,
      "git_repository_required": true
    }
  }
}
EOF
fi

echo "✅ Slash commands installed successfully!"
echo ""
echo "📍 Settings location: $SETTINGS_FILE"
echo ""
echo "Available slash commands:"
echo "  /actions          - Full GitHub Actions improvement"
echo "  /actions-create   - Create new workflows"
echo "  /actions-fix      - Fix failing workflows" 
echo "  /actions-improve  - Improve existing workflows"
echo "  /actions-security - Add security scanning"
echo "  /ci               - Quick CI workflow creation"
echo ""
echo "Usage in any Git repository:"
echo "  claude"
echo "  > /actions"
echo "  > /ci"
echo "  > /actions-security"
echo ""
echo "🎉 Ready to use! Navigate to any Git repository and use the slash commands."