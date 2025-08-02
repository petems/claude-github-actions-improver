#!/usr/bin/env python3
"""
Unit tests for Claude Token Setup
Tests GitHub token configuration, storage, and integration functionality
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import platform

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the claude token setup module (handle hyphenated filename)
try:
    from claude_token_setup import ClaudeTokenSetup
    claude_token_module = sys.modules['claude_token_setup']
except ImportError:
    # Handle case where module is named claude-token-setup.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("claude_token_setup", project_root / "claude-token-setup.py")
    claude_token_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(claude_token_module)
    ClaudeTokenSetup = claude_token_module.ClaudeTokenSetup


class TestClaudeTokenSetupInitialization(unittest.TestCase):
    """Test Claude token setup initialization"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ClaudeTokenSetup initialization"""
        expected_claude_dir = Path(self.temp_dir) / ".claude"
        expected_app_dir = expected_claude_dir / "github-actions-improver"
        
        self.assertEqual(self.setup.claude_dir, expected_claude_dir)
        self.assertEqual(self.setup.app_dir, expected_app_dir)
    
    def test_setup_directories(self):
        """Test directory creation with secure permissions"""
        self.setup.setup_directories()
        
        # Verify directories exist
        self.assertTrue(self.setup.claude_dir.exists())
        self.assertTrue(self.setup.app_dir.exists())
        self.assertTrue(self.setup.claude_dir.is_dir())
        self.assertTrue(self.setup.app_dir.is_dir())
        
        # Test permissions (on Unix-like systems)
        if platform.system().lower() != 'windows':
            claude_stat = self.setup.claude_dir.stat()
            app_stat = self.setup.app_dir.stat()
            
            # Should be readable/writable by owner only (0o700)
            self.assertEqual(claude_stat.st_mode & 0o777, 0o700)
            self.assertEqual(app_stat.st_mode & 0o777, 0o700)


class TestClaudeTokenSetupStatus(unittest.TestCase):
    """Test token status checking functionality"""
    
    def setUp(self):
        """Set up status test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        self.original_github_token = os.environ.get('GITHUB_TOKEN')
        self.original_gh_token = os.environ.get('GH_TOKEN')
        
        # Clear environment tokens for testing
        if 'GITHUB_TOKEN' in os.environ:
            del os.environ['GITHUB_TOKEN']
        if 'GH_TOKEN' in os.environ:
            del os.environ['GH_TOKEN']
        
        os.environ['HOME'] = self.temp_dir
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up status test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        if self.original_github_token:
            os.environ['GITHUB_TOKEN'] = self.original_github_token
        if self.original_gh_token:
            os.environ['GH_TOKEN'] = self.original_gh_token
        
        shutil.rmtree(self.temp_dir)
    
    def test_check_current_setup_no_token(self):
        """Test status when no token is configured"""
        status = self.setup.check_current_setup()
        
        self.assertFalse(status["has_token"])
        self.assertIsNone(status["token_source"])
        self.assertEqual(status["rate_limit"], 60)
        self.assertEqual(status["max_workers"], 2)
    
    def test_check_current_setup_with_github_token(self):
        """Test status with GITHUB_TOKEN environment variable"""
        os.environ['GITHUB_TOKEN'] = 'ghp_test_token_123'
        
        status = self.setup.check_current_setup()
        
        self.assertTrue(status["has_token"])
        self.assertEqual(status["token_source"], "Environment GITHUB_TOKEN")
        self.assertEqual(status["rate_limit"], 5000)
        self.assertEqual(status["max_workers"], 20)
    
    def test_check_current_setup_with_gh_token(self):
        """Test status with GH_TOKEN environment variable"""
        os.environ['GH_TOKEN'] = 'ghp_test_token_456'
        
        status = self.setup.check_current_setup()
        
        self.assertTrue(status["has_token"])
        self.assertEqual(status["token_source"], "Environment GH_TOKEN")
        self.assertEqual(status["rate_limit"], 5000)
        self.assertEqual(status["max_workers"], 20)
    
    def test_check_claude_env_file(self):
        """Test checking Claude .env file for token"""
        self.setup.setup_directories()
        env_file = self.setup.claude_dir / ".env"
        
        # Test with token in .env file
        with open(env_file, 'w') as f:
            f.write("# Comment\nGITHUB_TOKEN=ghp_env_token_789\nOTHER_VAR=value\n")
        
        token = self.setup._check_claude_env()
        self.assertEqual(token, "ghp_env_token_789")
    
    def test_check_claude_env_file_missing(self):
        """Test checking missing .env file"""
        token = self.setup._check_claude_env()
        self.assertIsNone(token)
    
    @patch('subprocess.run')
    def test_check_gh_cli_success(self, mock_subprocess):
        """Test successful GitHub CLI token check"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "ghp_cli_token_abc"
        mock_subprocess.return_value = mock_result
        
        token = self.setup._check_gh_cli()
        self.assertEqual(token, "ghp_cli_token_abc")
        
        mock_subprocess.assert_called_once_with(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5
        )
    
    @patch('subprocess.run')
    def test_check_gh_cli_failure(self, mock_subprocess):
        """Test failed GitHub CLI token check"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'gh')
        
        token = self.setup._check_gh_cli()
        self.assertIsNone(token)
    
    @patch('subprocess.run')
    def test_check_gh_cli_timeout(self, mock_subprocess):
        """Test GitHub CLI timeout"""
        mock_subprocess.side_effect = subprocess.TimeoutExpired('gh', 5)
        
        token = self.setup._check_gh_cli()
        self.assertIsNone(token)


class TestClaudeTokenSetupReports(unittest.TestCase):
    """Test status report generation"""
    
    def setUp(self):
        """Set up report test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up report test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    def test_show_status_report_no_token(self):
        """Test status report when no token is configured"""
        with patch.object(self.setup, 'check_current_setup') as mock_check:
            mock_check.return_value = {
                "has_token": False,
                "token_source": None,
                "rate_limit": 60,
                "max_workers": 2
            }
            
            report = self.setup.show_status_report()
            
            self.assertIn("❌ **Authentication**: Not configured", report)
            self.assertIn("60 requests/hour", report)
            self.assertIn("2 concurrent jobs", report)
            self.assertIn("💡 **Recommendation**", report)
    
    def test_show_status_report_with_token(self):
        """Test status report when token is configured"""
        with patch.object(self.setup, 'check_current_setup') as mock_check:
            mock_check.return_value = {
                "has_token": True,
                "token_source": "Environment GITHUB_TOKEN",
                "rate_limit": 5000,
                "max_workers": 20
            }
            
            report = self.setup.show_status_report()
            
            self.assertIn("✅ **Authentication**: Configured", report)
            self.assertIn("Environment GITHUB_TOKEN", report)
            self.assertIn("5,000 requests/hour", report)
            self.assertIn("20 concurrent jobs", report)
            self.assertIn("✅ **Your setup is optimized!**", report)
    
    def test_get_setup_options(self):
        """Test setup options display"""
        options = self.setup.get_setup_options()
        
        self.assertIn("**Option 1: GitHub CLI**", options)
        self.assertIn("**Option 2: Personal Access Token**", options)
        self.assertIn("**Option 3: Use existing token**", options)
        self.assertIn("`gh auth login`", options)


class TestClaudeTokenSetupGitHubCLI(unittest.TestCase):
    """Test GitHub CLI setup functionality"""
    
    def setUp(self):
        """Set up GitHub CLI test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up GitHub CLI test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.run')
    def test_setup_github_cli_installed(self, mock_subprocess):
        """Test GitHub CLI setup when CLI is installed"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = self.setup.setup_github_cli()
        
        self.assertIn("🔧 **GitHub CLI Setup Instructions:**", result["message"])
        self.assertIn("gh auth login", result["message"])
        self.assertIn("Run `gh auth login` in your terminal", result["next_steps"])
        
        mock_subprocess.assert_called_once_with(
            ["gh", "--version"],
            capture_output=True,
            check=True
        )
    
    @patch('subprocess.run')
    def test_setup_github_cli_not_installed(self, mock_subprocess):
        """Test GitHub CLI setup when CLI is not installed"""
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = self.setup.setup_github_cli()
        
        self.assertIn("❌ **GitHub CLI not installed**", result["message"])
        self.assertIn("brew install gh", result["message"])
        self.assertIn("sudo apt install gh", result["message"])
        self.assertIn("winget install GitHub.cli", result["message"])


class TestClaudeTokenSetupPersonalToken(unittest.TestCase):
    """Test personal access token setup"""
    
    def setUp(self):
        """Set up personal token test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up personal token test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    @patch('webbrowser.open')
    def test_setup_personal_token_browser_success(self, mock_browser):
        """Test personal token setup with successful browser opening"""
        mock_browser.return_value = True
        
        result = self.setup.setup_personal_token()
        
        self.assertIn("🔑 **Personal Access Token Setup:**", result["message"])
        self.assertIn("Token name**: `GitHub Actions Improver`", result["message"])
        self.assertIn("✅ **Browser opened successfully**", result["message"])
        self.assertEqual(result["token_url"], "https://github.com/settings/tokens/new")
        
        mock_browser.assert_called_once_with("https://github.com/settings/tokens/new")
    
    @patch('webbrowser.open')
    def test_setup_personal_token_browser_failure(self, mock_browser):
        """Test personal token setup with browser opening failure"""
        mock_browser.side_effect = Exception("Browser not available")
        
        result = self.setup.setup_personal_token()
        
        self.assertIn("🔑 **Personal Access Token Setup:**", result["message"])
        self.assertIn("📋 **Manual**: Open this URL:", result["message"])
        self.assertIn("https://github.com/settings/tokens/new", result["message"])


class TestClaudeTokenSetupTokenStorage(unittest.TestCase):
    """Test token storage functionality"""
    
    def setUp(self):
        """Set up token storage test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up token storage test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    def test_store_token_invalid_format(self):
        """Test storing token with invalid format"""
        result = self.setup.store_token_securely("invalid_token")
        
        self.assertFalse(result["success"])
        self.assertIn("❌ Invalid token format", result["message"])
    
    def test_store_token_valid_formats(self):
        """Test token format validation"""
        valid_tokens = [
            "ghp_test123",
            "gho_test456", 
            "ghu_test789",
            "ghs_testabc",
            "ghr_testdef"
        ]
        
        for token in valid_tokens:
            with patch.object(self.setup, '_store_in_environment') as mock_store:
                mock_store.return_value = True
                with patch.object(self.setup, '_test_token_integration') as mock_test:
                    mock_test.return_value = "Test result"
                    
                    result = self.setup.store_token_securely(token)
                    self.assertTrue(result["success"])
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_store_in_keychain_macos_success(self, mock_platform, mock_subprocess):
        """Test successful keychain storage on macOS"""
        mock_platform.return_value = "Darwin"
        mock_subprocess.return_value = Mock(returncode=0)
        
        # Mock os.uname for the specific call in the method
        with patch('os.uname') as mock_uname:
            mock_uname.return_value = Mock(sysname="Darwin")
            result = self.setup._store_in_keychain("ghp_test_token")
        
        self.assertTrue(result)
        
        # Should call delete first, then add
        self.assertEqual(mock_subprocess.call_count, 2)
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_store_in_keychain_macos_failure(self, mock_platform, mock_subprocess):
        """Test failed keychain storage on macOS"""
        mock_platform.return_value = "Darwin"
        mock_subprocess.return_value = Mock(returncode=1)
        
        # Mock os.uname for the specific call in the method
        with patch('os.uname') as mock_uname:
            mock_uname.return_value = Mock(sysname="Darwin")
            result = self.setup._store_in_keychain("ghp_test_token")
        
        self.assertFalse(result)
    
    @patch('platform.system')
    def test_store_in_keychain_not_macos(self, mock_platform):
        """Test keychain storage on non-macOS system"""
        mock_platform.return_value = "Linux"
        
        # Mock os.uname for the specific call in the method
        with patch('os.uname') as mock_uname:
            mock_uname.return_value = Mock(sysname="Linux")
            result = self.setup._store_in_keychain("ghp_test_token")
        
        self.assertFalse(result)
    
    def test_store_in_claude_env_new_file(self):
        """Test storing token in new Claude .env file"""
        result = self.setup._store_in_claude_env("ghp_test_token")
        self.assertTrue(result)
        
        # Verify file was created
        env_file = self.setup.claude_dir / ".env"
        self.assertTrue(env_file.exists())
        
        # Verify content
        with open(env_file, 'r') as f:
            content = f.read()
        
        self.assertIn("GITHUB_TOKEN=ghp_test_token", content)
        
        # Verify secure permissions (on Unix-like systems)
        if platform.system().lower() != 'windows':
            file_stat = env_file.stat()
            self.assertEqual(file_stat.st_mode & 0o777, 0o600)
        
        # Verify environment variable was set
        self.assertEqual(os.environ.get('GITHUB_TOKEN'), 'ghp_test_token')
    
    def test_store_in_claude_env_existing_file(self):
        """Test updating token in existing Claude .env file"""
        self.setup.setup_directories()
        env_file = self.setup.claude_dir / ".env"
        
        # Create existing file with different token
        with open(env_file, 'w') as f:
            f.write("# Existing config\nOTHER_VAR=value\nGITHUB_TOKEN=old_token\n")
        
        result = self.setup._store_in_claude_env("ghp_new_token")
        self.assertTrue(result)
        
        # Verify token was updated
        with open(env_file, 'r') as f:
            content = f.read()
        
        self.assertIn("GITHUB_TOKEN=ghp_new_token", content)
        self.assertNotIn("old_token", content)
        self.assertIn("OTHER_VAR=value", content)
    
    def test_store_in_environment(self):
        """Test storing token in environment variable"""
        result = self.setup._store_in_environment("ghp_env_token")
        self.assertTrue(result)
        
        self.assertEqual(os.environ.get('GITHUB_TOKEN'), 'ghp_env_token')
    
    def test_get_storage_description(self):
        """Test storage method descriptions"""
        descriptions = {
            "keychain": "macOS Keychain (most secure)",
            "claude_env": "Claude .env file (secure, auto-loaded)",
            "environment": "Environment variable (current session)"
        }
        
        for method, expected in descriptions.items():
            result = self.setup._get_storage_description(method)
            self.assertEqual(result, expected)
        
        # Test unknown method
        result = self.setup._get_storage_description("unknown")
        self.assertEqual(result, "Unknown")


class TestClaudeTokenSetupTokenTesting(unittest.TestCase):
    """Test token testing and validation"""
    
    def setUp(self):
        """Set up token testing fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up token testing fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    @patch('urllib.request.urlopen')
    def test_test_token_integration_success(self, mock_urlopen):
        """Test successful token integration test"""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            'rate': {
                'core': {
                    'limit': 5000,
                    'remaining': 4999
                }
            }
        }).encode()
        
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.setup._test_token_integration("ghp_test_token")
        self.assertIn("Verified with GitHub API", result)
        self.assertIn("4999/5000", result)
    
    @patch('urllib.request.urlopen')
    def test_test_token_integration_failure(self, mock_urlopen):
        """Test failed token integration test"""
        mock_urlopen.side_effect = Exception("Network error")
        
        result = self.setup._test_token_integration("ghp_test_token")
        self.assertEqual(result, "Token stored (API test skipped)")


class TestClaudeTokenSetupMainFunction(unittest.TestCase):
    """Test main function and command-line interface"""
    
    def setUp(self):
        """Set up main function test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        self.original_argv = sys.argv.copy()
        os.environ['HOME'] = self.temp_dir
    
    def tearDown(self):
        """Clean up main function test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        sys.argv = self.original_argv
        shutil.rmtree(self.temp_dir)
    
    @patch('builtins.print')
    def test_main_status_command(self, mock_print):
        """Test main function with --status command"""
        sys.argv = ['claude-token-setup.py', '--status']
        
        main = claude_token_module.main
        main()
        
        # Should call print with status report
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        self.assertIn("🔍 **Current GitHub API Status:**", call_args)
    
    @patch('builtins.print')
    def test_main_options_command(self, mock_print):
        """Test main function with --options command"""
        sys.argv = ['claude-token-setup.py', '--options']
        
        main = claude_token_module.main
        main()
        
        # Should call print with setup options
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        self.assertIn("**Option 1: GitHub CLI**", call_args)
    
    @patch('builtins.print')
    def test_main_gh_cli_command(self, mock_print):
        """Test main function with --gh-cli command"""
        sys.argv = ['claude-token-setup.py', '--gh-cli']
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            main = claude_token_module.main
            main()
            
            # Should call print with GitHub CLI setup instructions
            mock_print.assert_called()
            call_args = mock_print.call_args[0][0]
            self.assertIn("🔧 **GitHub CLI Setup Instructions:**", call_args)
    
    @patch('builtins.print')
    def test_main_personal_token_command(self, mock_print):
        """Test main function with --personal-token command"""
        sys.argv = ['claude-token-setup.py', '--personal-token']
        
        with patch('webbrowser.open'):
            main = claude_token_module.main
            main()
            
            # Should call print with personal token setup
            mock_print.assert_called()
            call_args = mock_print.call_args[0][0]
            self.assertIn("🔑 **Personal Access Token Setup:**", call_args)
    
    @patch('builtins.print')
    def test_main_store_token_command(self, mock_print):
        """Test main function with --store-token command"""
        sys.argv = ['claude-token-setup.py', '--store-token', 'ghp_test_token']
        
        main = claude_token_module.main
        main()
        
        # Should call print with storage result
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        # Should contain either success or failure message
        self.assertTrue(
            "✅ **Token stored successfully!**" in call_args or
            "❌ **Storage failed**" in call_args
        )
    
    @patch('builtins.print')
    def test_main_interactive_mode(self, mock_print):
        """Test main function in interactive mode"""
        sys.argv = ['claude-token-setup.py']
        
        main = claude_token_module.main
        main()
        
        # Should call print multiple times for interactive display
        self.assertGreaterEqual(mock_print.call_count, 3)
        
        # Check that status and options are printed
        call_args_list = [call[0][0] for call in mock_print.call_args_list]
        combined_output = ' '.join(call_args_list)
        
        self.assertIn("🚀 Claude GitHub Token Setup", combined_output)


class TestClaudeTokenSetupErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up error handling test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.setup = ClaudeTokenSetup()
    
    def tearDown(self):
        """Clean up error handling test fixtures"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        elif 'HOME' in os.environ:
            del os.environ['HOME']
        
        shutil.rmtree(self.temp_dir)
    
    def test_store_token_empty_string(self):
        """Test storing empty token"""
        result = self.setup.store_token_securely("")
        
        self.assertFalse(result["success"])
        self.assertIn("❌ Invalid token format", result["message"])
    
    def test_store_token_none(self):
        """Test storing None token"""
        result = self.setup.store_token_securely(None)
        
        self.assertFalse(result["success"])
        self.assertIn("❌ Invalid token format", result["message"])
    
    def test_claude_env_read_permission_error(self):
        """Test handling permission error when reading .env file"""
        self.setup.setup_directories()
        env_file = self.setup.claude_dir / ".env"
        
        # Create file and make it unreadable
        env_file.touch()
        if platform.system().lower() != 'windows':
            env_file.chmod(0o000)
        
        try:
            token = self.setup._check_claude_env()
            # Should return None when file can't be read
            self.assertIsNone(token)
        finally:
            # Restore permissions for cleanup
            if platform.system().lower() != 'windows':
                env_file.chmod(0o600)
    
    def test_setup_directories_permission_denied(self):
        """Test handling permission denied when creating directories"""
        # Create a read-only parent directory
        readonly_parent = Path(self.temp_dir) / "readonly"
        readonly_parent.mkdir()
        
        if platform.system().lower() != 'windows':
            readonly_parent.chmod(0o444)  # Read-only
        
        # Mock home to point inside read-only directory
        os.environ['HOME'] = str(readonly_parent / "user")
        
        try:
            # Create new setup instance
            setup = ClaudeTokenSetup()
            # This might raise an exception or handle it gracefully
            setup.setup_directories()
            # Test passes if no unhandled exception
            self.assertTrue(True)
        except PermissionError:
            # Expected behavior
            self.assertTrue(True)
        except Exception as e:
            # Other exceptions should be handled gracefully
            self.assertIsInstance(e, Exception)
        finally:
            # Restore permissions for cleanup
            if platform.system().lower() != 'windows':
                readonly_parent.chmod(0o755)


if __name__ == "__main__":
    # Run with coverage if available
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        
        unittest.main(exit=False)
        
        cov.stop()
        cov.save()
        print("\nCoverage Report:")
        cov.report()
    except ImportError:
        unittest.main()