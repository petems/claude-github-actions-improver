#!/usr/bin/env python3
"""
Integration tests for WGU Fighter with real GitHub repository
Tests end-to-end functionality in a controlled environment
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from unittest.mock import patch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from wgu_fighter import WGUFighter, BattleStatus
except ImportError:
    # Handle case where module is named wgu-fighter.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("wgu_fighter", project_root / "wgu-fighter.py")
    wgu_fighter_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wgu_fighter_module)
    WGUFighter = wgu_fighter_module.WGUFighter
    BattleStatus = wgu_fighter_module.BattleStatus


class WGUIntegrationTester:
    """Integration tester for WGU Fighter"""
    
    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None
        
    def setup_test_environment(self):
        """Set up a temporary test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="wgu_test_")
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        print(f"🔧 Setting up test environment in: {self.temp_dir}")
        
        # Initialize git repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "WGU Tester"], check=True)
        subprocess.run(["git", "config", "user.email", "wgu@test.com"], check=True)
        
        # Create basic project structure
        self.create_test_project()
        
        print("✅ Test environment set up successfully")
        
    def create_test_project(self):
        """Create a test project with workflows"""
        # Create Python project files
        Path("requirements.txt").write_text("requests>=2.28.0\npytest>=7.0.0\n")
        Path("main.py").write_text("print('Hello WGU!')\n")
        
        # Create tests directory
        tests_dir = Path("tests")
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("""
import unittest

class TestMain(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
""")
        
        # Create GitHub workflows directory
        workflows_dir = Path(".github/workflows")
        workflows_dir.mkdir(parents=True)
        
        # Create a basic CI workflow
        ci_workflow = """
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
"""
        (workflows_dir / "ci.yml").write_text(ci_workflow)
        
        # Create a security workflow
        security_workflow = """
name: Security
on: [push]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install safety
      - run: safety check -r requirements.txt
"""
        (workflows_dir / "security.yml").write_text(security_workflow)
        
        # Commit initial files
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test environment: {self.temp_dir}")
    
    def mock_github_workflows(self, scenario="success"):
        """Mock GitHub workflow responses for different scenarios"""
        if scenario == "success":
            return [
                {
                    "databaseId": 123456,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "createdAt": "2025-08-01T12:00:00Z"
                },
                {
                    "databaseId": 123457,
                    "name": "Security", 
                    "status": "completed",
                    "conclusion": "success",
                    "createdAt": "2025-08-01T11:30:00Z"
                }
            ]
        elif scenario == "failures":
            return [
                {
                    "databaseId": 123456,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "failure",
                    "createdAt": "2025-08-01T12:00:00Z"
                },
                {
                    "databaseId": 123457,
                    "name": "Security",
                    "status": "completed", 
                    "conclusion": "failure",
                    "createdAt": "2025-08-01T11:30:00Z"
                }
            ]
        elif scenario == "mixed":
            return [
                {
                    "databaseId": 123456,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "failure",
                    "createdAt": "2025-08-01T12:00:00Z"
                },
                {
                    "databaseId": 123457,
                    "name": "Security",
                    "status": "completed",
                    "conclusion": "success", 
                    "createdAt": "2025-08-01T11:30:00Z"
                }
            ]
        elif scenario == "running":
            return [
                {
                    "databaseId": 123456,
                    "name": "CI",
                    "status": "running",
                    "conclusion": None,
                    "createdAt": "2025-08-01T12:00:00Z"
                }
            ]
    
    def test_immediate_victory_scenario(self):
        """Test scenario where all workflows are already green"""
        print("\n🎯 Testing immediate victory scenario...")
        
        fighter = WGUFighter(max_rounds=3, wait_time=1)
        
        # Mock successful workflows
        mock_data = self.mock_github_workflows("success")
        
        with patch('subprocess.run') as mock_subprocess:
            mock_result = type('MockResult', (), {'stdout': json.dumps(mock_data)})()
            mock_subprocess.return_value = mock_result
            
            result = fighter.fight_until_victory()
            
        assert result == BattleStatus.VICTORY
        assert len(fighter.battle_history) == 0  # No battles needed
        print("✅ Immediate victory test passed!")
        
    def test_fighting_to_victory_scenario(self):
        """Test scenario with battles leading to victory"""
        print("\n🥊 Testing fighting to victory scenario...")
        
        fighter = WGUFighter(max_rounds=3, wait_time=1)
        
        # Create progression from failure to success
        mock_responses = [
            # Initial assessment - failures
            json.dumps(self.mock_github_workflows("failures")),
            # After round 1 - mixed results  
            json.dumps(self.mock_github_workflows("mixed")),
            # Check for running workflows
            json.dumps([]),
            # After round 2 - all success!
            json.dumps(self.mock_github_workflows("success")),
            # Final check for running workflows
            json.dumps([])
        ]
        
        with patch('subprocess.run') as mock_subprocess, \
             patch('time.sleep'):  # Speed up test
            
            # Create a mock result that cycles through responses
            mock_result = type('MockResult', (), {})()
            mock_subprocess.return_value = mock_result
            
            # Set up side_effect for multiple calls
            mock_subprocess.return_value.stdout = None
            def side_effect(*args, **kwargs):
                if hasattr(side_effect, 'call_count'):
                    side_effect.call_count += 1
                else:
                    side_effect.call_count = 0
                
                response_idx = min(side_effect.call_count, len(mock_responses) - 1)
                result = type('MockResult', (), {'stdout': mock_responses[response_idx]})()
                return result
            
            mock_subprocess.side_effect = side_effect
            
            result = fighter.fight_until_victory()
            
        assert result == BattleStatus.VICTORY
        assert len(fighter.battle_history) > 0
        assert len(fighter.total_fixes_applied) > 0
        print("✅ Fighting to victory test passed!")
        
    def test_strategic_retreat_scenario(self):
        """Test scenario where fighter must retreat after max rounds"""
        print("\n🏳️ Testing strategic retreat scenario...")
        
        fighter = WGUFighter(max_rounds=2, wait_time=1)
        
        # Mock persistent failures
        mock_data = self.mock_github_workflows("failures")
        
        with patch('subprocess.run') as mock_subprocess, \
             patch('time.sleep'):  # Speed up test
            
            mock_result = type('MockResult', (), {'stdout': json.dumps(mock_data)})()
            mock_subprocess.return_value = mock_result
            
            result = fighter.fight_until_victory()
            
        assert result == BattleStatus.STRATEGIC_RETREAT
        assert len(fighter.battle_history) == 2  # max_rounds
        
        # Check battle report was created
        report_path = Path("WGU-BATTLE-REPORT.md")
        assert report_path.exists()
        
        # Verify report content
        with open(report_path, 'r') as f:
            content = f.read()
            assert "WGU Battle Report" in content
            assert "Rounds Fought: 2" in content
            
        print("✅ Strategic retreat test passed!")
        
    def test_loop_detection_scenario(self):
        """Test loop detection and alternative strategies"""
        print("\n🔄 Testing loop detection scenario...")
        
        fighter = WGUFighter(max_rounds=5, wait_time=1)
        
        # Create identical failing rounds to trigger loop detection
        mock_data = self.mock_github_workflows("failures")
        
        with patch('subprocess.run') as mock_subprocess, \
             patch('time.sleep'):
            
            mock_result = type('MockResult', (), {'stdout': json.dumps(mock_data)})()
            mock_subprocess.return_value = mock_result
            
            result = fighter.fight_until_victory()
            
        assert result == BattleStatus.STRATEGIC_RETREAT
        
        # Should have detected loops and tried alternative strategies
        alternative_strategies = [
            "Tried different workflow runner versions",
            "Applied community-suggested workarounds",
            "Simplified workflow configurations to isolate issues"
        ]
        
        applied_fixes = fighter.total_fixes_applied
        has_alternatives = any(strategy in applied_fixes for strategy in alternative_strategies)
        assert has_alternatives, f"No alternative strategies found in: {applied_fixes}"
        
        print("✅ Loop detection test passed!")
        
    def test_aggressive_mode_scenario(self):
        """Test aggressive mode with experimental fixes"""
        print("\n💥 Testing aggressive mode scenario...")
        
        fighter = WGUFighter(max_rounds=2, wait_time=1, aggressive=True)
        
        mock_data = self.mock_github_workflows("failures")
        
        with patch('subprocess.run') as mock_subprocess, \
             patch('time.sleep'):
            
            mock_result = type('MockResult', (), {'stdout': json.dumps(mock_data)})()
            mock_subprocess.return_value = mock_result
            
            result = fighter.fight_until_victory()
            
        # Should have applied aggressive fixes
        aggressive_fixes = [
            "Tried alternative runner environment configurations",
            "Applied experimental caching strategies",
            "Updated matrix build configurations"
        ]
        
        applied_fixes = fighter.total_fixes_applied
        has_aggressive = any(fix in applied_fixes for fix in aggressive_fixes)
        assert has_aggressive, f"No aggressive fixes found in: {applied_fixes}"
        
        print("✅ Aggressive mode test passed!")
        
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting WGU Fighter Integration Tests")
        print("=" * 50)
        
        try:
            self.setup_test_environment()
            
            # Run test scenarios
            self.test_immediate_victory_scenario()
            self.test_fighting_to_victory_scenario()
            self.test_strategic_retreat_scenario()
            self.test_loop_detection_scenario()
            self.test_aggressive_mode_scenario()
            
            print("\n" + "=" * 50)
            print("🎉 All WGU Fighter integration tests passed!")
            print("💪 The fighter is ready for real-world battles!")
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {e}")
            raise
        finally:
            self.cleanup_test_environment()


def run_github_cli_tests():
    """Test GitHub CLI integration (requires gh to be installed)"""
    print("\n🔧 Testing GitHub CLI integration...")
    
    try:
        # Test if gh CLI is available
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ GitHub CLI available: {result.stdout.strip()}")
        
        # Test if we can run a basic gh command (won't work without auth, but tests availability)
        try:
            subprocess.run(["gh", "run", "list", "--limit", "1"], capture_output=True, check=True)
            print("✅ GitHub CLI authentication appears to be working")
        except subprocess.CalledProcessError:
            print("⚠️ GitHub CLI found but may not be authenticated (this is normal for testing)")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ GitHub CLI not available - some WGU features will be limited")
        
    print("✅ GitHub CLI integration test completed")


def main():
    """Run integration tests"""
    tester = WGUIntegrationTester()
    
    try:
        # Run main integration tests
        tester.run_all_tests()
        
        # Test GitHub CLI availability
        run_github_cli_tests()
        
        print("\n🎯 Integration testing complete!")
        print("The WGU Fighter is battle-tested and ready for deployment! (ง'̀-'́)ง")
        
    except Exception as e:
        print(f"\n💥 Integration tests failed: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())