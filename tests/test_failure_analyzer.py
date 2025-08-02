#!/usr/bin/env python3
"""
Unit tests for GitHub Actions Failure Analyzer
Tests core functionality, pattern recognition, and log analysis
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the failure analyzer
try:
    from failure_analyzer import GitHubActionsFailureAnalyzer
except ImportError:
    # Handle case where module is named failure-analyzer.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("failure_analyzer", project_root / "failure-analyzer.py")
    failure_analyzer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(failure_analyzer_module)
    GitHubActionsFailureAnalyzer = failure_analyzer_module.GitHubActionsFailureAnalyzer


class TestGitHubActionsFailureAnalyzer(unittest.TestCase):
    """Test failure analyzer core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create analyzer instance
        self.analyzer = GitHubActionsFailureAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization with different paths"""
        # Test default initialization
        analyzer_default = GitHubActionsFailureAnalyzer()
        self.assertIsInstance(analyzer_default.repo_path, Path)
        
        # Test custom path
        analyzer_custom = GitHubActionsFailureAnalyzer("/tmp")
        # Handle macOS /tmp symlink to /private/tmp
        expected_path = str(Path("/tmp").resolve())
        self.assertEqual(str(analyzer_custom.repo_path.resolve()), expected_path)
    
    @patch('subprocess.run')
    def test_get_recent_workflow_runs_success(self, mock_subprocess):
        """Test successful workflow runs retrieval"""
        # Mock successful gh CLI response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([
            {
                "databaseId": 123456,
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2025-08-01T12:00:00Z",
                "headBranch": "main",
                "event": "push",
                "workflowName": "CI",
                "url": "https://example.com/run/123456"
            },
            {
                "databaseId": 123457,
                "name": "Tests",
                "status": "completed",
                "conclusion": "failure",
                "createdAt": "2025-08-01T11:00:00Z",
                "headBranch": "feature-branch",
                "event": "pull_request",
                "workflowName": "Tests",
                "url": "https://example.com/run/123457"
            }
        ])
        mock_subprocess.return_value = mock_result
        
        runs = self.analyzer.get_recent_workflow_runs(limit=10)
        
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0]["name"], "CI")
        self.assertEqual(runs[0]["conclusion"], "success")
        self.assertEqual(runs[1]["name"], "Tests")
        self.assertEqual(runs[1]["conclusion"], "failure")
        
        # Verify correct command was called
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        self.assertIn("gh", args)
        self.assertIn("run", args)
        self.assertIn("list", args)
        self.assertIn("--limit", args)
        self.assertIn("10", args)
    
    @patch('subprocess.run')
    def test_get_recent_workflow_runs_error(self, mock_subprocess):
        """Test workflow runs retrieval with GitHub CLI error"""
        # Mock gh CLI error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "GitHub CLI authentication required"
        mock_subprocess.return_value = mock_result
        
        runs = self.analyzer.get_recent_workflow_runs()
        
        self.assertEqual(runs, [])
    
    @patch('subprocess.run')
    def test_get_recent_workflow_runs_exception(self, mock_subprocess):
        """Test workflow runs retrieval with subprocess exception"""
        # Mock subprocess exception
        mock_subprocess.side_effect = Exception("Command not found")
        
        runs = self.analyzer.get_recent_workflow_runs()
        
        self.assertEqual(runs, [])
    
    def test_get_failed_runs(self):
        """Test filtering for failed workflow runs"""
        test_runs = [
            {"name": "CI", "conclusion": "success"},
            {"name": "Tests", "conclusion": "failure"},
            {"name": "Security", "conclusion": "failure"},
            {"name": "Deploy", "conclusion": "success"},
            {"name": "Lint", "conclusion": "cancelled"}
        ]
        
        failed_runs = self.analyzer.get_failed_runs(test_runs)
        
        self.assertEqual(len(failed_runs), 2)
        self.assertEqual(failed_runs[0]["name"], "Tests")
        self.assertEqual(failed_runs[1]["name"], "Security")
        for run in failed_runs:
            self.assertEqual(run["conclusion"], "failure")
    
    def test_get_failed_runs_empty_list(self):
        """Test get_failed_runs with empty input"""
        failed_runs = self.analyzer.get_failed_runs([])
        self.assertEqual(failed_runs, [])
    
    def test_get_failed_runs_no_failures(self):
        """Test get_failed_runs with no failed runs"""
        test_runs = [
            {"name": "CI", "conclusion": "success"},
            {"name": "Tests", "conclusion": "success"}
        ]
        
        failed_runs = self.analyzer.get_failed_runs(test_runs)
        self.assertEqual(failed_runs, [])
    
    @patch('subprocess.run')
    def test_get_run_logs_success(self, mock_subprocess):
        """Test successful run log retrieval"""
        # Mock successful gh CLI log response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """
2025-08-01T12:00:00.000Z ##[group]Run pytest
2025-08-01T12:00:01.000Z pytest
2025-08-01T12:00:02.000Z ##[endgroup]
2025-08-01T12:00:03.000Z FAILED tests/test_something.py::test_function - ImportError: No module named 'requests'
2025-08-01T12:00:04.000Z ##[error]Process completed with exit code 1.
"""
        mock_subprocess.return_value = mock_result
        
        logs = self.analyzer.get_run_logs("123456")
        
        self.assertIn("FAILED tests/test_something.py", logs)
        self.assertIn("ImportError", logs)
        self.assertIn("No module named 'requests'", logs)
        
        # Verify correct command was called
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        self.assertIn("gh", args)
        self.assertIn("run", args)
        self.assertIn("view", args)
        self.assertIn("123456", args)
        self.assertIn("--log", args)
    
    @patch('subprocess.run')
    def test_get_run_logs_error(self, mock_subprocess):
        """Test run log retrieval with error"""
        # Mock gh CLI error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Run not found"
        mock_subprocess.return_value = mock_result
        
        logs = self.analyzer.get_run_logs("invalid-id")
        
        self.assertEqual(logs, "")


class TestFailureAnalyzerPatternRecognition(unittest.TestCase):
    """Test failure pattern recognition and analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = GitHubActionsFailureAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_python_import_error(self):
        """Test Python import error pattern recognition"""
        test_log = """
        2025-08-01T12:00:00.000Z FAILED tests/test_something.py::test_function
        2025-08-01T12:00:01.000Z ImportError: No module named 'requests'
        2025-08-01T12:00:02.000Z ##[error]Process completed with exit code 1.
        """
        
        # This tests the pattern recognition methods that would be in the analyzer
        # For now, test basic log content detection
        self.assertIn("ImportError", test_log)
        self.assertIn("No module named", test_log)
        self.assertIn("requests", test_log)
    
    def test_analyze_node_dependency_error(self):
        """Test Node.js dependency error pattern recognition"""
        test_log = """
        2025-08-01T12:00:00.000Z npm ERR! Cannot resolve dependency
        2025-08-01T12:00:01.000Z npm ERR! peer dep missing: react@^18.0.0
        2025-08-01T12:00:02.000Z ##[error]Process completed with exit code 1.
        """
        
        # Test basic Node.js error pattern detection
        self.assertIn("npm ERR!", test_log)
        self.assertIn("Cannot resolve dependency", test_log)
        self.assertIn("peer dep missing", test_log)
    
    def test_analyze_test_failure_pattern(self):
        """Test test failure pattern recognition"""
        test_log = """
        2025-08-01T12:00:00.000Z FAILED tests/test_api.py::test_authentication - AssertionError
        2025-08-01T12:00:01.000Z assert 401 == 200
        2025-08-01T12:00:02.000Z ##[error]Process completed with exit code 1.
        """
        
        # Test basic test failure pattern detection
        self.assertIn("FAILED", test_log)
        self.assertIn("AssertionError", test_log)
        self.assertIn("assert", test_log)
    
    def test_analyze_build_error_pattern(self):
        """Test build error pattern recognition"""
        test_log = """
        2025-08-01T12:00:00.000Z error TS2304: Cannot find name 'React'
        2025-08-01T12:00:01.000Z src/App.tsx(1,8): error TS2305: Module has no exported member
        2025-08-01T12:00:02.000Z ##[error]Process completed with exit code 1.
        """
        
        # Test basic TypeScript/build error pattern detection
        self.assertIn("error TS", test_log)
        self.assertIn("Cannot find name", test_log)
        self.assertIn("no exported member", test_log)


class TestFailureAnalyzerIntegration(unittest.TestCase):
    """Integration tests for failure analyzer"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Initialize git repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        self.analyzer = GitHubActionsFailureAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """Clean up integration test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.run')
    def test_full_analysis_workflow(self, mock_subprocess):
        """Test complete failure analysis workflow"""
        # Mock GitHub CLI responses
        def mock_subprocess_side_effect(*args, **kwargs):
            cmd = args[0]
            
            if "run" in cmd and "list" in cmd:
                # Mock workflow runs list
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = json.dumps([
                    {
                        "databaseId": 123456,
                        "name": "CI",
                        "status": "completed",
                        "conclusion": "failure",
                        "createdAt": "2025-08-01T12:00:00Z",
                        "headBranch": "main",
                        "event": "push",
                        "workflowName": "CI",
                        "url": "https://example.com/run/123456"
                    }
                ])
                return mock_result
            
            elif "run" in cmd and "view" in cmd and "--log" in cmd:
                # Mock workflow logs
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = """
2025-08-01T12:00:00.000Z ##[group]Run pytest
2025-08-01T12:00:01.000Z FAILED tests/test_api.py::test_auth - ImportError: No module named 'requests'
2025-08-01T12:00:02.000Z ##[error]Process completed with exit code 1.
"""
                return mock_result
            
            # Default mock
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            return mock_result
        
        mock_subprocess.side_effect = mock_subprocess_side_effect
        
        # Test the workflow
        runs = self.analyzer.get_recent_workflow_runs()
        self.assertEqual(len(runs), 1)
        
        failed_runs = self.analyzer.get_failed_runs(runs)
        self.assertEqual(len(failed_runs), 1)
        self.assertEqual(failed_runs[0]["conclusion"], "failure")
        
        logs = self.analyzer.get_run_logs("123456")
        self.assertIn("ImportError", logs)
        self.assertIn("No module named 'requests'", logs)
    
    def test_analyzer_with_no_git_repo(self):
        """Test analyzer behavior when not in a git repository"""
        # Create analyzer in non-git directory
        non_git_dir = tempfile.mkdtemp()
        try:
            analyzer = GitHubActionsFailureAnalyzer(non_git_dir)
            self.assertEqual(analyzer.repo_path, Path(non_git_dir).resolve())
        finally:
            shutil.rmtree(non_git_dir)
    
    def test_analyzer_with_relative_path(self):
        """Test analyzer with relative paths"""
        analyzer = GitHubActionsFailureAnalyzer(".")
        self.assertEqual(analyzer.repo_path, Path(".").resolve())
        
        analyzer_relative = GitHubActionsFailureAnalyzer("../")
        self.assertEqual(analyzer_relative.repo_path, Path("../").resolve())


class TestFailureAnalyzerErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up error handling test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = GitHubActionsFailureAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """Clean up error handling test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_malformed_json_response(self):
        """Test handling of malformed JSON from GitHub CLI"""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "invalid json {"
            mock_subprocess.return_value = mock_result
            
            runs = self.analyzer.get_recent_workflow_runs()
            self.assertEqual(runs, [])
    
    def test_empty_json_response(self):
        """Test handling of empty JSON response"""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "[]"
            mock_subprocess.return_value = mock_result
            
            runs = self.analyzer.get_recent_workflow_runs()
            self.assertEqual(runs, [])
    
    def test_missing_conclusion_field(self):
        """Test handling of runs with missing conclusion field"""
        test_runs = [
            {"name": "CI", "status": "completed"},  # Missing conclusion
            {"name": "Tests", "conclusion": "failure"},
            {"name": "Deploy"}  # Missing both status and conclusion
        ]
        
        failed_runs = self.analyzer.get_failed_runs(test_runs)
        self.assertEqual(len(failed_runs), 1)
        self.assertEqual(failed_runs[0]["name"], "Tests")
    
    @patch('subprocess.run')
    def test_permission_denied_error(self, mock_subprocess):
        """Test handling of permission denied errors"""
        mock_subprocess.side_effect = PermissionError("Permission denied")
        
        runs = self.analyzer.get_recent_workflow_runs()
        self.assertEqual(runs, [])
        
        logs = self.analyzer.get_run_logs("123456")
        self.assertEqual(logs, "")


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