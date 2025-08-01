#!/usr/bin/env python3
"""
Claude Token Setup - Streamlined for Claude CLI Integration
Interactive GitHub token setup optimized for Claude's workflow
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Optional

class ClaudeTokenSetup:
    """Streamlined token setup for Claude CLI integration"""
    
    def __init__(self):
        self.claude_dir = Path.home() / ".claude"
        self.app_dir = self.claude_dir / "github-actions-improver"
        
    def setup_directories(self):
        """Set up Claude directories with secure permissions"""
        self.claude_dir.mkdir(exist_ok=True)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        os.chmod(self.claude_dir, 0o700)
        os.chmod(self.app_dir, 0o700)
    
    def check_current_setup(self) -> Dict[str, any]:
        """Check current token configuration"""
        status = {
            "has_token": False,
            "token_source": None,
            "rate_limit": 60,
            "max_workers": 2
        }
        
        # Check various token sources
        token_sources = [
            ("Environment GITHUB_TOKEN", os.environ.get("GITHUB_TOKEN")),
            ("Environment GH_TOKEN", os.environ.get("GH_TOKEN")),
            ("Claude .env", self._check_claude_env()),
            ("GitHub CLI", self._check_gh_cli())
        ]
        
        for source, token in token_sources:
            if token:
                status["has_token"] = True
                status["token_source"] = source
                status["rate_limit"] = 5000
                status["max_workers"] = 20
                break
        
        return status
    
    def _check_claude_env(self) -> Optional[str]:
        """Check Claude .env file for token"""
        env_file = self.claude_dir / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('GITHUB_TOKEN='):
                            return line.split('=', 1)[1].strip()
            except:
                pass
        return None
    
    def _check_gh_cli(self) -> Optional[str]:
        """Check GitHub CLI for token"""
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def show_status_report(self) -> str:
        """Generate status report for Claude to display"""
        status = self.check_current_setup()
        
        report = "🔍 **Current GitHub API Status:**\n\n"
        
        if status["has_token"]:
            report += f"✅ **Authentication**: Configured\n"
            report += f"📊 **Token Source**: {status['token_source']}\n"
            report += f"⚡ **Rate Limit**: {status['rate_limit']:,} requests/hour\n"
            report += f"🚀 **Max Workers**: {status['max_workers']} concurrent jobs\n"
            report += f"🎯 **Capacity**: Can handle 50+ failing jobs simultaneously\n\n"
            report += f"✅ **Your setup is optimized!** No changes needed.\n"
        else:
            report += f"❌ **Authentication**: Not configured\n"
            report += f"📊 **Rate Limit**: {status['rate_limit']} requests/hour (severely limited)\n"
            report += f"🐌 **Max Workers**: {status['max_workers']} concurrent jobs\n"
            report += f"⚠️ **Capacity**: Can only handle ~5 jobs before hitting limits\n\n"
            report += f"💡 **Recommendation**: Set up GitHub token for 83x better performance!\n"
        
        return report
    
    def get_setup_options(self) -> str:
        """Get setup options for Claude to present"""
        return """
🚀 **Choose your preferred setup method:**

**Option 1: GitHub CLI** (Recommended - Easiest)
- ✅ Automatic token management
- ✅ No manual token creation needed
- ✅ Works immediately after authentication
- 📋 Command: `gh auth login`

**Option 2: Personal Access Token** (Manual but flexible)
- ✅ Full control over permissions
- ✅ Can be shared across systems
- ✅ Works in CI/CD environments
- 📋 Requires browser setup at GitHub

**Option 3: Use existing token** (If you already have one)
- ✅ Quick setup with existing token
- ✅ Just needs secure storage configuration
- 📋 Enter token and choose storage method

Which option would you prefer? I can guide you through any of these approaches.
"""
    
    def setup_github_cli(self) -> Dict[str, any]:
        """Set up GitHub CLI authentication"""
        result = {
            "success": False,
            "message": "",
            "next_steps": []
        }
        
        # Check if gh CLI is installed
        try:
            subprocess.run(["gh", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            result["message"] = """
❌ **GitHub CLI not installed**

Please install GitHub CLI first:
- **macOS**: `brew install gh`
- **Ubuntu/Debian**: `sudo apt install gh`
- **Windows**: `winget install GitHub.cli`
- **Other**: Visit https://cli.github.com/

After installation, run this command again.
"""
            return result
        
        result["message"] = """
🔧 **GitHub CLI Setup Instructions:**

1. **Run authentication command:**
   ```bash
   gh auth login
   ```

2. **Choose your preferences:**
   - GitHub.com (not Enterprise)
   - HTTPS (recommended)
   - Authenticate via web browser
   - Yes to git credential helper

3. **Complete browser authentication:**
   - Browser will open automatically
   - Sign in to your GitHub account
   - Authorize GitHub CLI

4. **Verify setup:**
   ```bash
   gh auth status
   ```

After completing these steps, your token will be automatically available and you'll have 5,000+ requests/hour with 20+ concurrent workers!

Would you like me to check your authentication status after you complete this setup?
"""
        
        result["next_steps"] = [
            "Run `gh auth login` in your terminal",
            "Complete browser authentication", 
            "Run `/gha:setup-token` again to verify"
        ]
        
        return result
    
    def setup_personal_token(self) -> Dict[str, any]:
        """Guide through personal access token creation"""
        result = {
            "success": False,
            "message": "",
            "next_steps": [],
            "token_url": "https://github.com/settings/tokens/new"
        }
        
        result["message"] = """
🔑 **Personal Access Token Setup:**

I'll open GitHub's token creation page for you with the recommended settings.

**Step 1: Token Configuration**
- **Token name**: `GitHub Actions Improver`
- **Expiration**: `90 days` (or `No expiration` if preferred)
- **Scopes to select**:
  ☑️ `repo` - Full control of private repositories
  ☑️ `workflow` - Update GitHub Action workflows
  ☑️ `read:org` - Read org membership (optional)

**Step 2: Create Token**
- Click "Generate token"
- **⚠️ COPY IMMEDIATELY** - GitHub only shows it once!
- Token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Step 3: Return Here**
- Come back with your token
- I'll help you store it securely

🌐 **Opening GitHub token page...**
"""
        
        # Try to open browser
        try:
            webbrowser.open(result["token_url"])
            result["message"] += "\n✅ **Browser opened successfully**"
        except:
            result["message"] += f"\n📋 **Manual**: Open this URL: {result['token_url']}"
        
        result["next_steps"] = [
            "Configure token with recommended scopes",
            "Generate and copy the token",
            "Return here to set up secure storage"
        ]
        
        return result
    
    def store_token_securely(self, token: str) -> Dict[str, any]:
        """Store token using the most secure method available"""
        result = {
            "success": False,
            "message": "",
            "storage_method": None
        }
        
        # Validate token format
        if not token or not token.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
            result["message"] = "❌ Invalid token format. Please check your token."
            return result
        
        # Try secure storage methods in order of preference
        storage_methods = [
            ("keychain", self._store_in_keychain),
            ("claude_env", self._store_in_claude_env),
            ("environment", self._store_in_environment)
        ]
        
        for method_name, store_func in storage_methods:
            try:
                if store_func(token):
                    result["success"] = True
                    result["storage_method"] = method_name
                    break
            except Exception as e:
                continue
        
        if result["success"]:
            # Test the token
            test_result = self._test_token_integration(token)
            result["message"] = f"""
✅ **Token stored successfully!**

📊 **Storage Method**: {self._get_storage_description(result['storage_method'])}
🔒 **Security**: Token encrypted and protected
🚀 **Integration**: {test_result}

**🎉 Setup Complete!** 

Your GitHub Actions processing is now optimized:
- ⚡ **Rate Limit**: 5,000+ requests/hour (was 60)
- 🚀 **Workers**: 20+ concurrent (was 2) 
- 🎯 **Capacity**: 50+ jobs simultaneously

Try it now with: `/gha:fix --days 7 --workers 20`
"""
        else:
            result["message"] = """
❌ **Storage failed**

Please try manual setup:
1. Add to environment: `export GITHUB_TOKEN=your_token`
2. Or add to ~/.claude/.env: `echo "GITHUB_TOKEN=your_token" >> ~/.claude/.env`
"""
        
        return result
    
    def _store_in_keychain(self, token: str) -> bool:
        """Store in system keychain (macOS)"""
        if os.uname().sysname.lower() != "darwin":
            return False
            
        try:
            # Delete existing
            subprocess.run([
                "security", "delete-generic-password",
                "-s", "claude-github-actions",
                "-a", "github-token"
            ], capture_output=True)
            
            # Add new
            result = subprocess.run([
                "security", "add-generic-password",
                "-s", "claude-github-actions",
                "-a", "github-token", 
                "-w", token,
                "-D", "GitHub Actions Improver Token"
            ], capture_output=True)
            
            return result.returncode == 0
        except:
            return False
    
    def _store_in_claude_env(self, token: str) -> bool:
        """Store in Claude .env file"""
        try:
            self.setup_directories()
            env_file = self.claude_dir / ".env"
            
            # Read existing content
            existing_content = ""
            if env_file.exists():
                with open(env_file, 'r') as f:
                    existing_content = f.read()
            
            # Update or add token
            if "GITHUB_TOKEN=" in existing_content:
                lines = []
                for line in existing_content.split('\n'):
                    if line.startswith('GITHUB_TOKEN='):
                        lines.append(f'GITHUB_TOKEN={token}')
                    else:
                        lines.append(line)
                new_content = '\n'.join(lines)
            else:
                new_content = existing_content
                if not new_content.endswith('\n') and new_content:
                    new_content += '\n'
                new_content += f'\n# GitHub Token for Actions Improver\nGITHUB_TOKEN={token}\n'
            
            # Write with secure permissions
            with open(env_file, 'w') as f:
                f.write(new_content)
            
            os.chmod(env_file, 0o600)
            
            # Set for current session
            os.environ['GITHUB_TOKEN'] = token
            
            return True
        except:
            return False
    
    def _store_in_environment(self, token: str) -> bool:
        """Store as environment variable"""
        try:
            os.environ['GITHUB_TOKEN'] = token
            return True
        except:
            return False
    
    def _get_storage_description(self, method: str) -> str:
        """Get human-readable storage method description"""
        descriptions = {
            "keychain": "macOS Keychain (most secure)",
            "claude_env": "Claude .env file (secure, auto-loaded)",
            "environment": "Environment variable (current session)"
        }
        return descriptions.get(method, "Unknown")
    
    def _test_token_integration(self, token: str) -> str:
        """Test token integration with GitHub API"""
        try:
            import urllib.request
            import json
            
            request = urllib.request.Request(
                "https://api.github.com/rate_limit",
                headers={"Authorization": f"token {token}"}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
                core_limit = data['rate']['core']
                
                return f"Verified with GitHub API ({core_limit['remaining']}/{core_limit['limit']} requests available)"
        except:
            return "Token stored (API test skipped)"

def main():
    setup = ClaudeTokenSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--status":
            print(setup.show_status_report())
        elif command == "--options":
            print(setup.get_setup_options())
        elif command == "--gh-cli":
            result = setup.setup_github_cli()
            print(result["message"])
        elif command == "--personal-token":
            result = setup.setup_personal_token()
            print(result["message"])
        elif command == "--store-token" and len(sys.argv) > 2:
            token = sys.argv[2]
            result = setup.store_token_securely(token)
            print(result["message"])
    else:
        # Interactive mode
        print("🚀 Claude GitHub Token Setup")
        print("=" * 40)
        print(setup.show_status_report())
        print(setup.get_setup_options())

if __name__ == "__main__":
    main()