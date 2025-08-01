#!/usr/bin/env python3
"""
Secure Configuration Manager for Claude GitHub Actions Improver
Handles secure storage and retrieval of GitHub tokens and configuration
Following Claude best practices for secret management
"""

import os
import json
import base64
import getpass
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureConfigManager:
    """Secure configuration management following Claude best practices"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.claude_config_dir = Path.home() / ".claude"
        self.app_config_dir = self.claude_config_dir / "github-actions-improver"
        self.config_file = self.app_config_dir / "config.json"
        self.secure_file = self.app_config_dir / "secure.enc"
        
        # Ensure directories exist
        self.app_config_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_encryption_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'claude-gha-salt'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def store_token_secure(self, token: str, token_type: str = "github", 
                          description: str = "GitHub Actions Improver") -> bool:
        """Store token using the most secure method available"""
        
        print("🔒 Choosing secure storage method...")
        
        # Method 1: System Keychain (Most Secure)
        if self._try_keychain_storage(token, token_type, description):
            return True
            
        # Method 2: Claude Config Directory with Encryption
        if self._try_encrypted_storage(token, token_type):
            return True
            
        # Method 3: Environment Variable (Fallback)
        return self._try_environment_storage(token, token_type)
    
    def _try_keychain_storage(self, token: str, token_type: str, description: str) -> bool:
        """Try to store in system keychain"""
        try:
            if self.system == "darwin":  # macOS
                return self._store_macos_keychain(token, token_type, description)
            elif self.system == "linux":  # Linux
                return self._store_linux_keyring(token, token_type, description)
            elif self.system == "windows":  # Windows
                return self._store_windows_credential(token, token_type, description)
        except Exception as e:
            print(f"⚠️ Keychain storage failed: {e}")
        return False
    
    def _store_macos_keychain(self, token: str, token_type: str, description: str) -> bool:
        """Store token in macOS Keychain"""
        service_name = f"claude-gha-{token_type}"
        account_name = "github-actions-improver"
        
        try:
            # Delete existing entry if it exists
            subprocess.run([
                "security", "delete-generic-password",
                "-s", service_name,
                "-a", account_name
            ], capture_output=True)
            
            # Add new entry
            result = subprocess.run([
                "security", "add-generic-password",
                "-s", service_name,
                "-a", account_name,
                "-w", token,
                "-D", description,
                "-T", "",  # Allow all applications
                "-U"  # Update if exists
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Token stored securely in macOS Keychain")
                self._save_config({"storage_method": "keychain", "service": service_name})
                return True
            else:
                print(f"❌ Keychain storage failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ macOS Keychain error: {e}")
            return False
    
    def _store_linux_keyring(self, token: str, token_type: str, description: str) -> bool:
        """Store token in Linux keyring using secret-tool"""
        try:
            # Check if secret-tool is available
            subprocess.run(["which", "secret-tool"], check=True, capture_output=True)
            
            service_name = f"claude-gha-{token_type}"
            
            result = subprocess.run([
                "secret-tool", "store",
                "--label", description,
                "service", service_name,
                "account", "github-actions-improver"
            ], input=token, text=True, capture_output=True)
            
            if result.returncode == 0:
                print(f"✅ Token stored securely in Linux keyring")
                self._save_config({"storage_method": "keyring", "service": service_name})
                return True
            else:
                print(f"❌ Keyring storage failed: {result.stderr}")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ secret-tool not available, trying alternative storage...")
            return False
    
    def _store_windows_credential(self, token: str, token_type: str, description: str) -> bool:
        """Store token in Windows Credential Manager"""
        try:
            import keyring
            service_name = f"claude-gha-{token_type}"
            keyring.set_password(service_name, "github-actions-improver", token)
            
            print(f"✅ Token stored securely in Windows Credential Manager")
            self._save_config({"storage_method": "credential_manager", "service": service_name})
            return True
            
        except ImportError:
            print("⚠️ keyring module not available, install with: pip install keyring")
            return False
        except Exception as e:
            print(f"❌ Windows credential storage error: {e}")
            return False
    
    def _try_encrypted_storage(self, token: str, token_type: str) -> bool:
        """Store token in encrypted file in Claude config directory"""
        try:
            print("🔐 Setting up encrypted storage in Claude config directory...")
            
            # Get password for encryption
            password = getpass.getpass("Enter a password to encrypt your token: ")
            if len(password) < 8:
                print("❌ Password too short (minimum 8 characters)")
                return False
            
            # Encrypt the token
            key = self._get_encryption_key(password)
            fernet = Fernet(key)
            
            encrypted_data = {
                "token": fernet.encrypt(token.encode()).decode(),
                "token_type": token_type,
                "created_at": str(os.path.getmtime),
                "encrypted": True
            }
            
            # Save encrypted data
            with open(self.secure_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            # Set restrictive permissions (owner only)
            os.chmod(self.secure_file, 0o600)
            
            print(f"✅ Token encrypted and stored in: {self.secure_file}")
            self._save_config({"storage_method": "encrypted_file", "file": str(self.secure_file)})
            return True
            
        except Exception as e:
            print(f"❌ Encrypted storage error: {e}")
            return False
    
    def _try_environment_storage(self, token: str, token_type: str) -> bool:
        """Store token as environment variable (least secure fallback)"""
        print("⚠️ Using environment variable storage (less secure)")
        print("💡 Consider setting up keychain/keyring for better security")
        
        env_var = f"GITHUB_TOKEN"
        
        # Set for current session
        os.environ[env_var] = token
        
        # Offer to add to shell config
        response = input("Add to shell configuration file? (y/n): ").lower()
        if response == 'y':
            return self._add_to_shell_config(env_var, token)
        else:
            print(f"✅ Token set for current session only")
            print(f"💡 To make permanent: export {env_var}={token}")
            self._save_config({"storage_method": "environment", "variable": env_var})
            return True
    
    def _add_to_shell_config(self, env_var: str, token: str) -> bool:
        """Add environment variable to shell configuration"""
        shell = os.environ.get('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            config_file = Path.home() / '.zshrc'
        elif 'bash' in shell:
            config_file = Path.home() / '.bashrc'  
        else:
            config_file = Path.home() / '.profile'
        
        try:
            with open(config_file, 'a') as f:
                f.write(f"\n# GitHub Token for Claude Actions Improver\n")
                f.write(f"export {env_var}={token}\n")
            
            print(f"✅ Added to {config_file}")
            print(f"💡 Restart terminal or run: source {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding to shell config: {e}")
            return False
    
    def retrieve_token(self, token_type: str = "github") -> Optional[str]:
        """Retrieve token using the configured storage method"""
        config = self._load_config()
        if not config:
            return self._try_fallback_retrieval(token_type)
        
        storage_method = config.get("storage_method")
        
        if storage_method == "keychain":
            return self._retrieve_from_keychain(config.get("service"))
        elif storage_method == "keyring":
            return self._retrieve_from_keyring(config.get("service"))
        elif storage_method == "credential_manager":
            return self._retrieve_from_credential_manager(config.get("service"))
        elif storage_method == "encrypted_file":
            return self._retrieve_from_encrypted_file(config.get("file"))
        elif storage_method == "environment":
            return self._retrieve_from_environment(config.get("variable"))
        
        return self._try_fallback_retrieval(token_type)
    
    def _retrieve_from_keychain(self, service_name: str) -> Optional[str]:
        """Retrieve token from macOS Keychain"""
        try:
            result = subprocess.run([
                "security", "find-generic-password",
                "-s", service_name,
                "-a", "github-actions-improver",
                "-w"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"⚠️ Token not found in keychain: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Keychain retrieval error: {e}")
            return None
    
    def _retrieve_from_keyring(self, service_name: str) -> Optional[str]:
        """Retrieve token from Linux keyring"""
        try:
            result = subprocess.run([
                "secret-tool", "lookup",
                "service", service_name,
                "account", "github-actions-improver"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
                
        except Exception:
            return None
    
    def _retrieve_from_encrypted_file(self, file_path: str) -> Optional[str]:
        """Retrieve token from encrypted file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)
            
            if not encrypted_data.get("encrypted"):
                return None
            
            password = getpass.getpass("Enter password to decrypt token: ")
            key = self._get_encryption_key(password)
            fernet = Fernet(key)
            
            encrypted_token = encrypted_data["token"].encode()
            decrypted_token = fernet.decrypt(encrypted_token).decode()
            
            return decrypted_token
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
    
    def _retrieve_from_environment(self, env_var: str) -> Optional[str]:
        """Retrieve token from environment variable"""
        return os.environ.get(env_var)
    
    def _try_fallback_retrieval(self, token_type: str) -> Optional[str]:
        """Try fallback methods to find token"""
        # Try common environment variables
        env_vars = ["GITHUB_TOKEN", "GH_TOKEN", "GITHUB_ACCESS_TOKEN"]
        for var in env_vars:
            token = os.environ.get(var)
            if token:
                print(f"🔍 Found token in environment variable: {var}")
                return token
        
        # Try GitHub CLI
        try:
            result = subprocess.run(["gh", "auth", "token"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("🔍 Found token from GitHub CLI")
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def _save_config(self, config_data: Dict[str, Any]) -> None:
        """Save configuration metadata"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            print(f"⚠️ Could not save config: {e}")
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration metadata"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def show_storage_status(self) -> None:
        """Show current token storage configuration"""
        print("🔒 Token Storage Status")
        print("=" * 40)
        
        config = self._load_config()
        if config:
            method = config.get("storage_method", "unknown")
            print(f"📊 Storage Method: {method}")
            
            if method == "keychain":
                print(f"🔑 Service: {config.get('service')}")
                print(f"🍎 Location: macOS Keychain")
            elif method == "keyring":
                print(f"🔑 Service: {config.get('service')}")
                print(f"🐧 Location: Linux Keyring")
            elif method == "encrypted_file":
                print(f"📁 File: {config.get('file')}")
                print(f"🔐 Encryption: PBKDF2 + Fernet")
            elif method == "environment":
                print(f"🌍 Variable: {config.get('variable')}")
                print(f"⚠️ Security: Low (plaintext)")
        else:
            print("❌ No stored configuration found")
        
        # Check if token is accessible
        token = self.retrieve_token()
        if token:
            print(f"✅ Token Status: Accessible")
            print(f"🔍 Length: {len(token)} characters")
            print(f"📝 Preview: {token[:8]}...{token[-4:]}")
        else:
            print(f"❌ Token Status: Not accessible")
    
    def cleanup_storage(self) -> bool:
        """Remove stored tokens and configuration"""
        print("🧹 Cleaning up stored tokens...")
        
        config = self._load_config()
        if config:
            method = config.get("storage_method")
            
            if method == "keychain" and self.system == "darwin":
                service = config.get("service")
                subprocess.run([
                    "security", "delete-generic-password",
                    "-s", service,
                    "-a", "github-actions-improver"
                ], capture_output=True)
                print("✅ Removed from macOS Keychain")
                
            elif method == "encrypted_file":
                file_path = config.get("file")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print("✅ Removed encrypted file")
        
        # Remove config files
        if self.config_file.exists():
            os.remove(self.config_file)
            print("✅ Removed configuration")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Secure Configuration Manager')
    parser.add_argument('--store', help='Store a new token')
    parser.add_argument('--retrieve', action='store_true', help='Retrieve stored token')
    parser.add_argument('--status', action='store_true', help='Show storage status')
    parser.add_argument('--cleanup', action='store_true', help='Remove stored data')
    
    args = parser.parse_args()
    
    manager = SecureConfigManager()
    
    if args.store:
        manager.store_token_secure(args.store)
    elif args.retrieve:
        token = manager.retrieve_token()
        if token:
            print(f"Token: {token}")
        else:
            print("No token found")
    elif args.status:
        manager.show_storage_status()
    elif args.cleanup:
        manager.cleanup_storage()
    else:
        manager.show_storage_status()

if __name__ == "__main__":
    main()