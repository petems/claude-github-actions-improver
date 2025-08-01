#!/usr/bin/env python3
"""
Claude Configuration Setup
Sets up secure configuration directory following Claude best practices
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

def setup_claude_config():
    """Set up Claude configuration directory structure"""
    
    # Claude configuration directory
    claude_dir = Path.home() / ".claude"
    app_dir = claude_dir / "github-actions-improver"
    
    print("🔧 Setting up Claude configuration directory...")
    print(f"📁 Location: {claude_dir}")
    
    # Create directories
    claude_dir.mkdir(exist_ok=True)
    app_dir.mkdir(exist_ok=True)
    
    # Set secure permissions (owner only)
    os.chmod(claude_dir, 0o700)
    os.chmod(app_dir, 0o700)
    
    # Create .env file for environment variables
    env_file = claude_dir / ".env"
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# Claude Environment Variables\n")
            f.write("# This file is automatically loaded by Claude\n\n")
            f.write("# GitHub Token (uncomment and set your token)\n")
            f.write("# GITHUB_TOKEN=your_token_here\n\n")
        
        os.chmod(env_file, 0o600)
        print(f"✅ Created secure .env file: {env_file}")
    
    # Create app-specific config
    config_file = app_dir / "config.json"
    default_config = {
        "version": "1.0",
        "api_settings": {
            "default_workers": 8,
            "rate_limit_buffer": 0.1,
            "timeout_seconds": 30
        },
        "storage_settings": {
            "prefer_keychain": True,
            "encrypt_files": True,
            "secure_permissions": True
        },
        "workflow_settings": {
            "default_days": 14,
            "auto_fix_confidence": 0.8,
            "backup_before_fix": True
        }
    }
    
    if not config_file.exists():
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        os.chmod(config_file, 0o600)
        print(f"✅ Created app configuration: {config_file}")
    
    # Create gitignore for the directory
    gitignore_file = claude_dir / ".gitignore"
    if not gitignore_file.exists():
        with open(gitignore_file, 'w') as f:
            f.write("# Claude Configuration Security\n")
            f.write("*.enc\n")
            f.write("*.key\n")
            f.write(".env\n")
            f.write("secrets/\n")
            f.write("tokens/\n")
        
        print(f"✅ Created security .gitignore: {gitignore_file}")
    
    # Create README for the configuration
    readme_file = app_dir / "README.md"
    if not readme_file.exists():
        with open(readme_file, 'w') as f:
            f.write("""# Claude GitHub Actions Improver Configuration

This directory contains secure configuration for the GitHub Actions Improver.

## Files:
- `config.json` - Application settings
- `secure.enc` - Encrypted token storage (if used)
- `.env` - Environment variables (auto-loaded by Claude)

## Security:
- All files have restrictive permissions (600/700)
- Tokens are stored using system keychain when possible
- Fallback to encrypted storage in this directory
- Never commit tokens to version control

## Usage:
- Claude automatically loads `.env` from `~/.claude/.env`
- App-specific settings stored in this directory
- Tokens retrieved automatically by the system
""")
        print(f"✅ Created documentation: {readme_file}")
    
    print(f"\n🎉 Claude configuration setup complete!")
    print(f"📁 Configuration directory: {app_dir}")
    print(f"🔒 Security: Owner-only permissions set")
    print(f"💡 Claude will automatically load: {claude_dir}/.env")

if __name__ == "__main__":
    setup_claude_config()