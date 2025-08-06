#!/bin/bash
# GitHub Actions Improver - Enhanced Installation Script
# Inspired by ClaudePreference methodology

set -euo pipefail

# Version and metadata
readonly SCRIPT_VERSION="2.0.0"
readonly TOOL_NAME="GitHub Actions Improver"
readonly REPO_URL="https://github.com/petems/claude-github-actions-improver"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Default configuration
DEFAULT_INSTALL_DIR="$HOME/.claude/actions-improver"
BACKUP_DIR=""
FORCE_INSTALL=false
DRY_RUN=false
VERBOSE=false
UPDATE_MODE=false
UNINSTALL_MODE=false
ROLLBACK_MODE=false

# Global variables
INSTALL_DIR="$DEFAULT_INSTALL_DIR"
CLAUDE_SETTINGS_DIR=""
CLAUDE_COMMANDS_DIR=""
BACKUP_TIMESTAMP=""
MANIFEST_FILE=""

# Utility functions
log_info() { 
    echo -e "${BLUE}[INFO]${NC} $1" 
}

log_success() { 
    echo -e "${GREEN}[SUCCESS]${NC} $1" 
}

log_warning() { 
    echo -e "${YELLOW}[WARNING]${NC} $1" 
}

log_error() { 
    echo -e "${RED}[ERROR]${NC} $1" 
}

log_debug() { 
    [[ "$VERBOSE" == true ]] && echo -e "${PURPLE}[DEBUG]${NC} $1" 
}

log_step() { 
    echo -e "${CYAN}▶${NC} $1" 
}

# Help function
show_help() {
    cat << EOF
${TOOL_NAME} Installation Script v${SCRIPT_VERSION}

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -d, --directory DIR     Install directory (default: $DEFAULT_INSTALL_DIR)
    -f, --force            Force overwrite existing installation
    -n, --dry-run          Preview installation without making changes
    -v, --verbose          Enable verbose output
    -u, --update           Update existing installation
    -r, --rollback         Rollback to previous backup
    --uninstall            Remove installation completely
    -h, --help             Show this help message

EXAMPLES:
    $0                              # Standard installation
    $0 -d ~/.local/claude-actions   # Custom directory
    $0 --dry-run --verbose          # Preview with detailed output
    $0 --update                     # Update existing installation
    $0 --rollback                   # Restore previous backup

For more information, visit: $REPO_URL
EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--directory)
                INSTALL_DIR="$2"
                shift 2
                ;;
            -f|--force)
                FORCE_INSTALL=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -u|--update)
                UPDATE_MODE=true
                shift
                ;;
            -r|--rollback)
                ROLLBACK_MODE=true
                shift
                ;;
            --uninstall)
                UNINSTALL_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# System checks
check_prerequisites() {
    log_step "Checking system prerequisites..."
    
    # Check for required commands
    local required_commands=("git" "python3" "curl")
    local missing_required=0
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' not found"
            missing_required=1
        else
            log_debug "Found $cmd: $(command -v "$cmd")"
        fi
    done
    if [[ $missing_required -eq 1 ]]; then
        return 1
    fi
    
    # Check Claude CLI (optional)
    if ! command -v claude &> /dev/null; then
        log_warning "Claude CLI not found. Please install from: https://docs.anthropic.com/claude/docs"
        log_warning "Installation will continue, but commands won't work without Claude CLI"
    else
        log_debug "Found Claude CLI: $(command -v claude)"
        local claude_version
        claude_version=$(timeout 5 claude --version 2>/dev/null || echo "unknown")
        log_debug "Claude CLI version: $claude_version"
    fi
    
    # Check GitHub CLI (optional)
    if command -v gh &> /dev/null; then
        log_debug "Found GitHub CLI: $(command -v gh)"
        local gh_version
        gh_version=$(timeout 5 gh --version 2>/dev/null | head -n1 || echo "unknown")
        log_debug "GitHub CLI version: $gh_version"
    else
        log_warning "GitHub CLI not found. Some features (failure analysis) require 'gh'"
        log_warning "Install with: brew install gh (macOS) or sudo apt install gh (Ubuntu)"
    fi
    
    log_success "System prerequisites checked"
    return 0
}

# Detect Claude commands directories
detect_claude_settings() {
    log_step "Detecting Claude commands directories..."
    
    # Global commands directory
    if [[ "$OSTYPE" == "darwin"* ]]; then
        CLAUDE_SETTINGS_DIR="$HOME/Library/Application Support/claude"
    else
        CLAUDE_SETTINGS_DIR="$HOME/.config/claude"
    fi
    
    CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"
    
    log_debug "Claude settings directory: $CLAUDE_SETTINGS_DIR"
    log_debug "Claude commands directory: $CLAUDE_COMMANDS_DIR"
    
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$CLAUDE_COMMANDS_DIR"
        log_info "Created Claude commands directory: $CLAUDE_COMMANDS_DIR"
    fi
}

# Create backup
create_backup() {
    if [[ ! -d "$INSTALL_DIR" ]] && [[ ! -f "$CLAUDE_SETTINGS_DIR/settings.json" ]]; then
        log_debug "No existing installation found, skipping backup"
        return 0
    fi
    
    BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_DIR="${INSTALL_DIR}.backup.$BACKUP_TIMESTAMP"
    
    log_step "Creating backup..."
    
    if [[ "$DRY_RUN" == false ]]; then
        if [[ -d "$INSTALL_DIR" ]]; then
            cp -r "$INSTALL_DIR" "$BACKUP_DIR"
            log_success "Installation backed up to: $BACKUP_DIR"
        fi
        
        if [[ -f "$CLAUDE_SETTINGS_DIR/settings.json" ]]; then
            cp "$CLAUDE_SETTINGS_DIR/settings.json" "$BACKUP_DIR/settings.json.backup" 2>/dev/null || true
            log_success "Claude settings backed up"
        fi
    else
        log_info "[DRY RUN] Would create backup at: $BACKUP_DIR"
    fi
}

# Install command files
install_commands() {
    log_step "Installing command files..."
    
    local claude_commands_dir="$HOME/.claude/commands/gha"
    local local_commands_dir="$INSTALL_DIR/commands"
    
    if [[ "$DRY_RUN" == false ]]; then
        # Create Claude commands directory with gha subdirectory
        mkdir -p "$claude_commands_dir"
        mkdir -p "$local_commands_dir"
        
        # Copy command files to Claude's commands/gha directory
        if [[ -d "commands" ]]; then
            cp commands/*.md "$claude_commands_dir/"
            log_success "Command files installed to Claude commands directory: $claude_commands_dir"
            
            # Also keep a copy in our install directory for reference
            cp -r commands/* "$local_commands_dir/"
            log_success "Command files backed up to: $local_commands_dir"
        else
            log_error "Commands directory not found in source"
            return 1
        fi
        
        # Copy scripts
        local scripts=("claude-agent-github-actions-enhanced.py" "failure-analyzer.py" "github-actions-improver-minimal.py" "interactive-gha-analyzer.py" "github-token-generator.py" "api-limit-handler.py" "enhanced-concurrent-fixer.py" "claude-token-setup.py" "secure-config-manager.py" "claude-config-setup.py" "wgu-fighter.py")
        for script in "${scripts[@]}"; do
            if [[ -f "$script" ]]; then
                cp "$script" "$INSTALL_DIR/"
                chmod +x "$INSTALL_DIR/$script"
                log_debug "Installed script: $script"
            fi
        done
        
        # Copy templates
        if [[ -d "templates" ]]; then
            cp -r templates "$INSTALL_DIR/"
            log_success "Templates installed"
        fi
        
        # Copy documentation
        local docs=("README.md" "FAILURE-ANALYSIS.md" "SLASH-COMMANDS.md" "CLAUDE.md")
        mkdir -p "$INSTALL_DIR/docs"
        for doc in "${docs[@]}"; do
            if [[ -f "$doc" ]]; then
                cp "$doc" "$INSTALL_DIR/docs/"
                log_debug "Installed documentation: $doc"
            fi
        done
        
    else
        log_info "[DRY RUN] Would install commands to: $claude_commands_dir"
        log_info "[DRY RUN] Would backup commands to: $local_commands_dir"
    fi
}

# Update Claude settings (no longer needed with commands directory)
update_claude_settings() {
    log_step "Commands installed to ~/.claude/commands directory..."
    log_success "Commands will be automatically discovered by Claude CLI"
}

# Create installation manifest
create_manifest() {
    MANIFEST_FILE="$INSTALL_DIR/.installation_manifest"
    
    if [[ "$DRY_RUN" == false ]]; then
        cat > "$MANIFEST_FILE" << EOF
# GitHub Actions Improver Installation Manifest
INSTALLATION_DATE=$(date -Iseconds)
INSTALLATION_VERSION=$SCRIPT_VERSION
INSTALL_DIRECTORY=$INSTALL_DIR
CLAUDE_SETTINGS_DIR=$CLAUDE_SETTINGS_DIR
CLAUDE_COMMANDS_DIR=$CLAUDE_COMMANDS_DIR
BACKUP_DIRECTORY=$BACKUP_DIR
USER=$(whoami)
HOSTNAME=$(hostname)
OS_TYPE=$OSTYPE
SCRIPT_PATH=$(realpath "$0")
EOF
        log_debug "Installation manifest created: $MANIFEST_FILE"
    fi
}

# Add to PATH
add_to_path() {
    log_step "Adding to PATH..."
    
    local shell_rc=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        shell_rc="$HOME/.bashrc"
    else
        shell_rc="$HOME/.profile"
    fi
    
    local path_entry="export PATH=\"$INSTALL_DIR:\$PATH\""
    
    if [[ "$DRY_RUN" == false ]]; then
        if ! grep -q "$INSTALL_DIR" "$shell_rc" 2>/dev/null; then
            echo "" >> "$shell_rc"
            echo "# GitHub Actions Improver" >> "$shell_rc"
            echo "$path_entry" >> "$shell_rc"
            log_success "Added to PATH in: $shell_rc"
            log_info "Restart your shell or run: source $shell_rc"
        else
            log_info "PATH already contains install directory"
        fi
    else
        log_info "[DRY RUN] Would add to PATH: $path_entry"
    fi
}

# Rollback function
rollback_installation() {
    log_step "Rolling back installation..."
    
    # Find most recent backup
    local latest_backup
    latest_backup=$(find "$(dirname "$INSTALL_DIR")" -name "$(basename "$INSTALL_DIR").backup.*" -type d 2>/dev/null | sort -r | head -n1)
    
    if [[ -z "$latest_backup" ]]; then
        log_error "No backup found for rollback"
        return 1
    fi
    
    log_info "Found backup: $latest_backup"
    
    if [[ "$DRY_RUN" == false ]]; then
        # Remove current installation
        if [[ -d "$INSTALL_DIR" ]]; then
            rm -rf "$INSTALL_DIR"
        fi
        
        # Restore from backup
        mv "$latest_backup" "$INSTALL_DIR"
        
        # Restore settings if available
        if [[ -f "$INSTALL_DIR/settings.json.backup" ]]; then
            cp "$INSTALL_DIR/settings.json.backup" "$CLAUDE_SETTINGS_DIR/settings.json"
            log_success "Claude settings restored"
        fi
        
        log_success "Installation rolled back successfully"
    else
        log_info "[DRY RUN] Would rollback from: $latest_backup"
    fi
}

# Uninstall function
uninstall() {
    log_step "Uninstalling GitHub Actions Improver..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Remove installation directory
        if [[ -d "$INSTALL_DIR" ]]; then
            rm -rf "$INSTALL_DIR"
            log_success "Removed installation directory: $INSTALL_DIR"
        fi
        
        # Remove from PATH
        local shell_files=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
        for shell_file in "${shell_files[@]}"; do
            if [[ -f "$shell_file" ]] && grep -q "$INSTALL_DIR" "$shell_file"; then
                # Create backup
                cp "$shell_file" "$shell_file.backup.$(date +%Y%m%d_%H%M%S)"
                # Remove PATH entry
                grep -v "$INSTALL_DIR" "$shell_file" > "$shell_file.tmp"
                mv "$shell_file.tmp" "$shell_file"
                log_success "Removed from PATH in: $shell_file"
            fi
        done
        
        # Clean up command files from Claude commands directory
        local claude_commands_dir="$HOME/.claude/commands/gha"
        if [[ -d "$claude_commands_dir" ]]; then
            rm -rf "$claude_commands_dir"
            log_success "Removed GHA commands from $claude_commands_dir"
        fi
        
        log_success "Uninstallation complete"
    else
        log_info "[DRY RUN] Would remove installation and clean up settings"
    fi
}

# Main installation function
main_install() {
    log_info "Starting installation of $TOOL_NAME v$SCRIPT_VERSION"
    
    check_prerequisites || { log_error "System prerequisites not met. Aborting."; return 1; }
    detect_claude_settings
    
    if [[ "$UPDATE_MODE" == true ]]; then
        log_info "Running in update mode"
    elif [[ "$FORCE_INSTALL" == false ]] && [[ -d "$INSTALL_DIR" ]]; then
        log_error "Installation directory already exists: $INSTALL_DIR"
        log_info "Use --force to overwrite or --update to update existing installation"
        return 1
    fi
    
    create_backup
    install_commands || { log_error "Failed to install commands."; return 1; }
    update_claude_settings || { log_error "Failed to update Claude settings."; return 1; }
    create_manifest
    add_to_path
    
    log_success "Installation completed successfully!"
    echo
    log_info "Installation directory: $INSTALL_DIR"
    log_info "Commands directory: $CLAUDE_COMMANDS_DIR"
    log_info "Available commands:"
    echo -e "  ${CYAN}/gha:fix${NC}        - Intelligent failure analysis and fixing"
    echo -e "  ${CYAN}/gha:create${NC}     - Smart workflow creation for your project"
    echo -e "  ${CYAN}/gha:analyze${NC}    - Comprehensive performance and security analysis"
    echo -e "  ${CYAN}/gha:setup-token${NC} - GitHub token setup for enhanced API access"
    echo -e "  ${CYAN}/gha:wgu${NC}        - Won't Give Up persistent fighter (ง'̀-'́)ง"
    echo
    log_info "Usage: Navigate to any Git repository and run 'claude', then use the slash commands"
    log_info "Note: Command files installed as Markdown files in ~/.claude/commands/"
    echo
    if [[ -n "$BACKUP_DIR" ]]; then
        log_info "Backup created at: $BACKUP_DIR"
    fi
}

# Main execution
main() {
    parse_arguments "$@"
    
    if [[ "$ROLLBACK_MODE" == true ]]; then
        rollback_installation || { log_error "Rollback failed."; exit 1; }
    elif [[ "$UNINSTALL_MODE" == true ]]; then
        uninstall || { log_error "Uninstall failed."; exit 1; }
    else
        main_install || { log_error "Installation failed."; exit 1; }
    fi
}

# Execute main function with all arguments
main "$@"