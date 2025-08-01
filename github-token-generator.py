#!/usr/bin/env python3
"""
GitHub Token Generator Helper
Interactive tool to help users create and configure GitHub tokens for API access
"""

import os
import sys
import json
import time
import subprocess
import webbrowser
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import argparse

class GitHubTokenGenerator:
    """Interactive GitHub token generation and setup helper"""
    
    def __init__(self):
        self.token_types = {
            'personal': {
                'name': 'Personal Access Token (Classic)',
                'limit': '5,000 requests/hour',
                'recommended_for': 'Individual developers, small teams',
                'scopes': ['repo', 'actions:read', 'workflow'],
                'url': 'https://github.com/settings/tokens',
                'difficulty': 'Easy'
            },
            'fine_grained': {
                'name': 'Fine-grained Personal Access Token',
                'limit': '5,000 requests/hour', 
                'recommended_for': 'Granular permissions, specific repos',
                'scopes': ['Actions:read', 'Contents:read', 'Metadata:read'],
                'url': 'https://github.com/settings/personal-access-tokens/new',
                'difficulty': 'Medium'
            },
            'github_app': {
                'name': 'GitHub App Installation Token',
                'limit': '15,000+ requests/hour',
                'recommended_for': 'Organizations, CI/CD systems',
                'scopes': ['Actions:read', 'Contents:read', 'Issues:read'],
                'url': 'https://github.com/settings/apps',
                'difficulty': 'Advanced'
            },
            'github_cli': {
                'name': 'GitHub CLI Authentication',
                'limit': '5,000 requests/hour',
                'recommended_for': 'Quick setup, local development',
                'scopes': 'Automatic based on usage',
                'url': 'Command line only',
                'difficulty': 'Easiest'
            }
        }
    
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step_num: int, title: str, description: str = ""):
        """Print formatted step"""
        print(f"\n📋 STEP {step_num}: {title}")
        if description:
            print(f"   {description}")
        print("-" * 50)
    
    def show_token_comparison(self):
        """Show comparison of different token types"""
        self.print_header("GitHub Token Options Comparison")
        
        print("Choose the best token type for your needs:\n")
        
        for key, token_info in self.token_types.items():
            difficulty_color = {
                'Easiest': '🟢',
                'Easy': '🟡', 
                'Medium': '🟠',
                'Advanced': '🔴'
            }
            
            print(f"{difficulty_color.get(token_info['difficulty'], '⚪')} **{token_info['name']}**")
            print(f"   • Rate Limit: {token_info['limit']}")
            print(f"   • Best For: {token_info['recommended_for']}")
            print(f"   • Difficulty: {token_info['difficulty']}")
            print()
    
    def generate_personal_token_interactive(self) -> str:
        """Interactive personal access token generation"""
        self.print_header("Personal Access Token Generation")
        
        print("This will guide you through creating a Personal Access Token (Classic)")
        print("Perfect for individual use with 5,000 requests/hour limit.\n")
        
        input("Press Enter to continue...")
        
        self.print_step(1, "Open GitHub Token Settings", 
                       "Opening GitHub token creation page in your browser...")
        
        token_url = "https://github.com/settings/tokens/new"
        
        # Try to open browser
        try:
            webbrowser.open(token_url)
            print(f"✅ Opened: {token_url}")
        except:
            print(f"📋 Manual: Open this URL in your browser:")
            print(f"   {token_url}")
        
        self.print_step(2, "Configure Token Settings")
        print("In the GitHub token creation form:")
        print("   1. **Token Name**: GitHub Actions Improver")
        print("   2. **Expiration**: 90 days (or No expiration)")
        print("   3. **Select Scopes**: Check the following boxes:")
        
        required_scopes = [
            ("repo", "Full control of private repositories"),
            ("workflow", "Update GitHub Action workflows"), 
            ("read:org", "Read org and team membership (optional)"),
            ("read:user", "Read user profile data (optional)")
        ]
        
        for scope, description in required_scopes:
            print(f"      ☑️  {scope} - {description}")
        
        print(f"\n   4. Click 'Generate token' button")
        
        self.print_step(3, "Copy Your Token")
        print("⚠️  IMPORTANT: Copy the token immediately!")
        print("   GitHub will only show it once for security reasons.")
        print("   The token will look like: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        
        # Get token from user
        print(f"\n📋 Paste your token here:")
        token = input("Token: ").strip()
        
        if not token:
            print("❌ No token provided. Exiting...")
            return ""
        
        if not token.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
            print("⚠️  Warning: Token doesn't look like a valid GitHub token")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                return ""
        
        # Validate token
        if self.validate_token(token):
            print("✅ Token validated successfully!")
            return token
        else:
            print("❌ Token validation failed. Please check and try again.")
            return ""
    
    def setup_github_cli_auth(self) -> bool:
        """Set up GitHub CLI authentication"""
        self.print_header("GitHub CLI Authentication Setup")
        
        print("GitHub CLI provides the easiest way to authenticate.")
        print("It handles token creation and storage automatically.\n")
        
        # Check if gh is installed
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub CLI is already installed")
                print(f"   Version: {result.stdout.strip()}")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            print("❌ GitHub CLI not found. Installing...")
            return self.install_github_cli()
        
        self.print_step(1, "Authenticate with GitHub")
        print("Running: gh auth login")
        print("This will open your browser for authentication...\n")
        
        try:
            # Run gh auth login interactively
            result = subprocess.run(['gh', 'auth', 'login'], 
                                  input='\n', text=True)
            
            if result.returncode == 0:
                print("✅ GitHub CLI authentication successful!")
                
                # Test the authentication
                test_result = subprocess.run(['gh', 'auth', 'status'], 
                                           capture_output=True, text=True)
                if test_result.returncode == 0:
                    print("✅ Authentication verified:")
                    print(f"   {test_result.stdout.strip()}")
                    return True
                else:
                    print("⚠️  Authentication may have issues:")
                    print(f"   {test_result.stderr}")
                    return False
            else:
                print("❌ GitHub CLI authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return False
    
    def install_github_cli(self) -> bool:
        """Install GitHub CLI based on platform"""
        self.print_header("GitHub CLI Installation")
        
        system = sys.platform.lower()
        
        if system == 'darwin':  # macOS
            print("📦 Installing GitHub CLI on macOS...")
            commands = [
                "brew install gh",  # Homebrew
                "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg"  # Manual
            ]
            
            print("Choose installation method:")
            print("1. Homebrew (recommended): brew install gh")
            print("2. Manual installer from: https://cli.github.com/")
            
        elif system.startswith('linux'):  # Linux
            print("📦 Installing GitHub CLI on Linux...")
            print("Choose your distribution:")
            print("1. Ubuntu/Debian: sudo apt install gh")
            print("2. Red Hat/CentOS: sudo yum install gh") 
            print("3. Arch Linux: sudo pacman -S github-cli")
            print("4. Manual installer: https://cli.github.com/")
            
        elif system.startswith('win'):  # Windows
            print("📦 Installing GitHub CLI on Windows...")
            print("Choose installation method:")
            print("1. Winget: winget install --id GitHub.cli")
            print("2. Chocolatey: choco install gh")
            print("3. Scoop: scoop install gh")
            print("4. Manual installer: https://cli.github.com/")
        
        print(f"\n💡 After installation, run this script again with --setup-cli")
        return False
    
    def validate_token(self, token: str) -> bool:
        """Validate GitHub token by making API call"""
        print("🔍 Validating token...")
        
        try:
            url = "https://api.github.com/user"
            headers = {
                "Authorization": f"token {token}",
                "User-Agent": "GitHub-Actions-Improver/1.0"
            }
            
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    print(f"✅ Token valid for user: {data.get('login', 'Unknown')}")
                    
                    # Check rate limits
                    limit_url = "https://api.github.com/rate_limit"
                    limit_request = urllib.request.Request(limit_url, headers=headers)
                    with urllib.request.urlopen(limit_request, timeout=10) as limit_response:
                        limit_data = json.loads(limit_response.read().decode())
                        core_limit = limit_data['rate']['core']
                        print(f"📊 Rate limit: {core_limit['remaining']}/{core_limit['limit']} requests remaining")
                        
                    return True
                else:
                    print(f"❌ Token validation failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            return False
    
    def save_token_configuration(self, token: str, method: str) -> bool:
        """Save token configuration using secure methods"""
        self.print_header("Token Configuration")
        
        print("🔒 Using secure storage methods (Claude best practices):\n")
        print("1. System Keychain/Keyring (most secure)")
        print("2. Claude config directory with encryption")
        print("3. Claude .env file (secure, auto-loaded)")
        print("4. Environment variable (current session)")
        print("5. Display only (manual setup)")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == '1':
            return self.save_to_secure_storage(token, method)
        elif choice == '2':
            return self.save_to_encrypted_claude_config(token)
        elif choice == '3':
            return self.save_to_claude_env(token)
        elif choice == '4':
            return self.save_to_environment(token)
        elif choice == '5':
            return self.display_token_usage(token)
        else:
            print("Invalid choice. Using secure storage...")
            return self.save_to_secure_storage(token, method)
    
    def save_to_environment(self, token: str) -> bool:
        """Save token to environment variable"""
        print("📝 Setting environment variable...")
        
        # Set for current session
        os.environ['GITHUB_TOKEN'] = token
        
        print("✅ Token set for current session")
        print(f"💡 To make permanent, add this to your shell config:")
        print(f"   export GITHUB_TOKEN={token}")
        
        return True
    
    def save_to_shell_config(self, token: str) -> bool:
        """Save token to shell configuration file"""
        shell = os.environ.get('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            config_file = os.path.expanduser('~/.zshrc')
        elif 'bash' in shell:
            config_file = os.path.expanduser('~/.bashrc')
        else:
            config_file = os.path.expanduser('~/.profile')
        
        print(f"📝 Adding token to {config_file}...")
        
        try:
            with open(config_file, 'a') as f:
                f.write(f"\n# GitHub Token for Actions Improver\n")
                f.write(f"export GITHUB_TOKEN={token}\n")
            
            print(f"✅ Token added to {config_file}")
            print(f"💡 Restart your terminal or run: source {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to shell config: {e}")
            return False
    
    def save_to_env_file(self, token: str) -> bool:
        """Save token to project .env file"""
        env_file = os.path.join(os.getcwd(), '.env')
        
        print(f"📝 Creating .env file: {env_file}")
        
        try:
            with open(env_file, 'a') as f:
                f.write(f"\n# GitHub Token for Actions Improver\n")
                f.write(f"GITHUB_TOKEN={token}\n")
            
            print(f"✅ Token saved to .env file")
            print(f"💡 Load with: source .env")
            print(f"⚠️  Don't commit .env to version control!")
            
            # Create .gitignore entry
            gitignore_file = os.path.join(os.getcwd(), '.gitignore')
            if os.path.exists(gitignore_file):
                with open(gitignore_file, 'r') as f:
                    if '.env' not in f.read():
                        with open(gitignore_file, 'a') as f:
                            f.write('\n.env\n')
                        print("✅ Added .env to .gitignore")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving to .env file: {e}")
            return False
    
    def display_token_usage(self, token: str) -> bool:
        """Display token usage instructions"""
        print("📋 Token Usage Instructions:")
        print("-" * 40)
        
        print(f"🔑 Your GitHub Token:")
        print(f"   {token}")
        
        print(f"\n💻 Usage Examples:")
        print(f"   # Environment variable:")
        print(f"   export GITHUB_TOKEN={token}")
        print(f"   claude --print '/gha:fix --days 7'")
        print(f"")
        print(f"   # Direct parameter:")
        print(f"   python3 enhanced-concurrent-fixer.py --token {token}")
        print(f"")
        print(f"   # In scripts:")
        print(f"   GITHUB_TOKEN={token} python3 your-script.py")
        
        print(f"\n⚠️  Security Notes:")
        print(f"   • Never commit tokens to version control")
        print(f"   • Tokens expire - set calendar reminder")
        print(f"   • Revoke old tokens when creating new ones")
        
        return True
    
    def test_token_with_concurrent_fixer(self, token: str) -> bool:
        """Test the token with our concurrent job fixer"""
        self.print_header("Testing Token with GitHub Actions Improver")
        
        print("🧪 Testing token with actual API calls...")
        
        try:
            # Set token in environment
            os.environ['GITHUB_TOKEN'] = token
            
            # Import our API handler
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("api_limit_handler", "api-limit-handler.py")
            api_limit_handler = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(api_limit_handler)
            
            handler = api_limit_handler.GitHubAPILimitHandler(token)
            summary = handler.get_api_limits_summary()
            
            print(f"✅ Token Integration Test Results:")
            print(f"   • Authentication: {summary['authenticated']}")
            print(f"   • Token Type: {summary['token_type']}")
            print(f"   • Rate Limit: {summary['rate_limit']['remaining']}/{summary['rate_limit']['limit']}")
            print(f"   • Recommended Workers: {summary['recommendations']['max_workers']}")
            
            print(f"\n🚀 Ready to process GitHub Actions jobs!")
            print(f"   Run: claude --print '/gha:fix --days 7 --workers {summary['recommendations']['max_workers']}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            return False
    
    def interactive_setup(self) -> str:
        """Main interactive setup flow"""
        self.print_header("GitHub Token Generator & Setup")
        
        print("Welcome! This tool will help you create and configure a GitHub token")
        print("for enhanced GitHub Actions analysis with higher API rate limits.\n")
        
        # Show options
        self.show_token_comparison()
        
        print("Choose your preferred method:")
        print("1. 🟢 GitHub CLI (Easiest - recommended)")
        print("2. 🟡 Personal Access Token (Manual)")
        print("3. 🟠 Fine-grained Token (Advanced)")
        print("4. ❓ Help me choose")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == '1':
            if self.setup_github_cli_auth():
                print("\n✅ GitHub CLI authentication complete!")
                print("🚀 Your token is ready to use automatically.")
                return "github_cli"
            else:
                print("\n❌ GitHub CLI setup failed. Try manual token creation.")
                return ""
                
        elif choice == '2':
            token = self.generate_personal_token_interactive()
            if token:
                self.save_token_configuration(token, 'personal')
                self.test_token_with_concurrent_fixer(token)
                return token
            else:
                return ""
                
        elif choice == '3':
            print("🟠 Fine-grained tokens require advanced GitHub knowledge.")
            print("   Visit: https://github.com/settings/personal-access-tokens/new")
            print("   Configure repository access and permissions manually.")
            return ""
            
        elif choice == '4':
            return self.help_choose_token_type()
        
        else:
            print("Invalid choice. Please run the script again.")
            return ""
    
    def help_choose_token_type(self) -> str:
        """Help user choose the right token type"""
        self.print_header("Token Type Recommendation")
        
        print("Answer a few questions to get a personalized recommendation:\n")
        
        # Usage questions
        usage = input("How will you use this? (personal/team/organization): ").lower()
        frequency = input("How often will you analyze workflows? (daily/weekly/monthly): ").lower()
        repo_count = input("How many repositories will you analyze? (1-5/6-20/20+): ")
        
        print(f"\n🎯 Recommendation based on your answers:")
        
        if usage in ['personal'] and frequency in ['weekly', 'monthly'] and '1-5' in repo_count:
            print("✅ **GitHub CLI** (recommended)")
            print("   • Perfect for individual use")
            print("   • Easy setup and maintenance")
            print("   • 5,000 requests/hour is plenty")
            choice = input("\nSet up GitHub CLI now? (y/n): ")
            if choice.lower() == 'y':
                return self.setup_github_cli_auth()
                
        elif usage in ['team', 'organization'] or '20+' in repo_count:
            print("✅ **Personal Access Token** (recommended)")
            print("   • Better for team environments")
            print("   • More control over permissions")
            print("   • Can be shared securely")
            choice = input("\nCreate Personal Access Token now? (y/n): ")
            if choice.lower() == 'y':
                token = self.generate_personal_token_interactive()
                if token:
                    self.save_token_configuration(token, 'personal')
                    return token
        
        else:
            print("✅ **GitHub CLI** (recommended for beginners)")
            print("   • Easiest to set up")
            print("   • Handles authentication automatically")
            
        return ""
    
    def save_to_secure_storage(self, token: str, method: str) -> bool:
        """Save token using system keychain/keyring"""
        try:
            print("🔒 Attempting to use system keychain/keyring...")
            
            system = os.uname().sysname.lower() if hasattr(os, 'uname') else 'unknown'
            
            if system == "darwin":  # macOS
                return self._store_macos_keychain(token)
            elif system == "linux":  # Linux  
                return self._store_linux_keyring(token)
            else:
                print("⚠️ System keychain not supported, using Claude .env")
                return self.save_to_claude_env(token)
                
        except Exception as e:
            print(f"❌ Secure storage failed: {e}")
            return self.save_to_claude_env(token)
    
    def _store_macos_keychain(self, token: str) -> bool:
        """Store in macOS Keychain"""
        try:
            service_name = "claude-github-actions"
            account_name = "github-token"
            
            # Delete existing
            subprocess.run([
                "security", "delete-generic-password",
                "-s", service_name, "-a", account_name
            ], capture_output=True)
            
            # Add new
            result = subprocess.run([
                "security", "add-generic-password",
                "-s", service_name, "-a", account_name,
                "-w", token, "-D", "GitHub Actions Improver Token"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Token stored in macOS Keychain")
                return True
            else:
                print(f"❌ Keychain failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ macOS Keychain error: {e}")
            return False
    
    def _store_linux_keyring(self, token: str) -> bool:
        """Store in Linux keyring"""
        try:
            result = subprocess.run([
                "secret-tool", "store",
                "--label", "GitHub Actions Improver Token",
                "service", "claude-github-actions",
                "account", "github-token"
            ], input=token, text=True, capture_output=True)
            
            if result.returncode == 0:
                print("✅ Token stored in Linux keyring")
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def save_to_claude_env(self, token: str) -> bool:
        """Save token to Claude .env file (auto-loaded by Claude)"""
        try:
            from pathlib import Path
            
            claude_dir = Path.home() / ".claude"
            claude_dir.mkdir(exist_ok=True)
            
            env_file = claude_dir / ".env"
            
            print(f"📝 Saving to Claude .env file: {env_file}")
            
            # Read existing content
            existing_content = ""
            if env_file.exists():
                with open(env_file, 'r') as f:
                    existing_content = f.read()
            
            # Check if GITHUB_TOKEN already exists
            if "GITHUB_TOKEN=" in existing_content:
                # Replace existing token
                lines = []
                for line in existing_content.split('\n'):
                    if line.startswith('GITHUB_TOKEN='):
                        lines.append(f'GITHUB_TOKEN={token}')
                    else:
                        lines.append(line)
                new_content = '\n'.join(lines)
            else:
                # Add new token
                new_content = existing_content
                if not new_content.endswith('\n') and new_content:
                    new_content += '\n'
                new_content += f'\n# GitHub Token for Actions Improver\nGITHUB_TOKEN={token}\n'
            
            # Write with secure permissions
            with open(env_file, 'w') as f:
                f.write(new_content)
            
            os.chmod(env_file, 0o600)  # Owner read/write only
            
            print(f"✅ Token saved to Claude .env file")
            print(f"🔒 File permissions set to 600 (owner only)")
            print(f"🚀 Claude will automatically load this token")
            
            # Set for current session too
            os.environ['GITHUB_TOKEN'] = token
            print(f"✅ Token also set for current session")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving to Claude .env: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='GitHub Token Generator for Actions Improver')
    parser.add_argument('--setup-cli', action='store_true', help='Set up GitHub CLI authentication')
    parser.add_argument('--validate-token', help='Validate an existing token')
    parser.add_argument('--quick-setup', action='store_true', help='Quick interactive setup')
    
    args = parser.parse_args()
    
    generator = GitHubTokenGenerator()
    
    if args.setup_cli:
        generator.setup_github_cli_auth()
    elif args.validate_token:
        if generator.validate_token(args.validate_token):
            print("✅ Token is valid and ready to use!")
        else:
            print("❌ Token validation failed")
    elif args.quick_setup:
        result = generator.interactive_setup()
        if result:
            print(f"\n🎉 Setup complete! Token ready to use.")
        else:
            print(f"\n❌ Setup incomplete. Please try again.")
    else:
        # Full interactive mode
        result = generator.interactive_setup()
        if result:
            print(f"\n🎉 Congratulations! Your GitHub token is ready.")
            print(f"🚀 You can now run GitHub Actions analysis with higher rate limits!")
        else:
            print(f"\n💡 Need help? Run with --help to see all options.")

if __name__ == "__main__":
    main()