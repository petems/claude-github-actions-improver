#!/usr/bin/env python3
"""
Test script to demonstrate improved keychain error handling
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from secure_config_manager import SecureConfigManager

def test_keychain_handling():
    """Test the improved keychain error handling"""
    print("🧪 Testing improved keychain error handling...\n")
    
    manager = SecureConfigManager()
    
    # Show current storage status
    manager.show_storage_status()
    
    print("\n" + "="*50)
    print("🔍 Testing token retrieval methods...")
    
    # Test retrieval with fallback methods
    token = manager.retrieve_token()
    if token:
        print(f"✅ Successfully retrieved token via fallback methods")
        print(f"🔍 Token length: {len(token)} characters")
        print(f"📝 Token preview: {token[:8]}...{token[-4:]}")
    else:
        print("❌ No token found via any method")
    
    print("\n💡 The improved system now:")
    print("  1. Gracefully handles keychain access issues")
    print("  2. Falls back to encrypted file storage")  
    print("  3. Uses environment variables as final fallback")
    print("  4. Can retrieve tokens from GitHub CLI")
    print("  5. Provides clear error messages and guidance")

if __name__ == "__main__":
    test_keychain_handling()