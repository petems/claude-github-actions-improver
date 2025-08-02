#!/usr/bin/env python3
"""
Unit tests for GitHub Actions Jobs Commands
Tests the core functionality of jobs-status, jobs-failed-investigate, and jobs-fixfailed-ngu commands
"""

import os
import sys
import unittest
import json
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from io import StringIO

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test fixtures
from tests.test_fixtures.github_api_responses import (
    get_sample_runs_data, get_sample_log_npm_error, get_sample_log_python_import_error,
    get_sample_log_test_assertion_error, get_sample_log_docker_error, 
    get_sample_log_cache_warning, get_sample_log_complex_multi_error,
    EXPECTED_FAILURE_PATTERNS
)

# Import the module under test
from gha_jobs_commands import (
    GitHubActionsJobsManager, JobsStatusCommand, JobsFailedInvestigateCommand,
    JobsFixFailedNGUCommand, WorkflowRun, FailurePattern, InvestigationResult,
    RunStatus, FixConfidence
)


class TestWorkflowRun(unittest.TestCase):
    """Test WorkflowRun dataclass"""
    
    def setUp(self):
        self.sample_run = WorkflowRun(
            id="12345",
            name="CI",
            status="completed",
            conclusion="failure",
            created_at="2024-08-02T10:00:00Z",
            head_branch="main",
            event="push",
            url="https://github.com/test/repo/actions/runs/12345"
        )
    
    def test_is_failed_property(self):
        """Test is_failed property correctly identifies failed runs"""
        # Test failure
        self.assertTrue(self.sample_run.is_failed)
        
        # Test cancelled (also considered failed)
        cancelled_run = WorkflowRun(
            id="12346", name="CI", status="completed", conclusion="cancelled",
            created_at="2024-08-02T10:00:00Z", head_branch="main", event="push"
        )
        self.assertTrue(cancelled_run.is_failed)
        
        # Test success
        success_run = WorkflowRun(
            id="12347", name="CI", status="completed", conclusion="success",
            created_at="2024-08-02T10:00:00Z", head_branch="main", event="push"
        )
        self.assertFalse(success_run.is_failed)
    
    def test_age_hours_calculation(self):
        """Test age calculation in hours"""
        # Use a fixed datetime string that we know works
        # This represents a time 1 hour ago in UTC
        from datetime import timezone
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        run = WorkflowRun(
            id="12345", name="CI", status="completed", conclusion="failure",
            created_at=one_hour_ago.isoformat().replace('+00:00', 'Z'), 
            head_branch="main", event="push"
        )
        
        # Age should be approximately 1 hour (allow broader tolerance for test stability)
        age = run.age_hours
        self.assertGreater(age, 0.8)  # More tolerant for test stability
        self.assertLess(age, 1.5)


class TestGitHubActionsJobsManager(unittest.TestCase):
    """Test GitHubActionsJobsManager core functionality"""
    
    def setUp(self):
        self.manager = GitHubActionsJobsManager()
    
    def test_failure_patterns_loaded(self):
        """Test that failure patterns are loaded on initialization"""
        patterns = self.manager.failure_patterns
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        # Check that patterns have required fields
        for pattern in patterns:
            self.assertIn("name", pattern)
            self.assertIn("regex", pattern) 
            self.assertIn("confidence", pattern)
            self.assertIn("description", pattern)
            self.assertIn("fix", pattern)
    
    @patch('subprocess.run')
    def test_get_recent_runs_success(self, mock_run):
        """Test successful retrieval of recent runs"""
        # Mock successful GitHub CLI response
        mock_result = Mock()
        mock_result.stdout = json.dumps(get_sample_runs_data())
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        runs = self.manager.get_recent_runs(limit=5)
        
        # Verify GitHub CLI was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertIn("gh", call_args)
        self.assertIn("run", call_args)
        self.assertIn("list", call_args)
        
        # Verify results
        self.assertEqual(len(runs), 5)
        self.assertIsInstance(runs[0], WorkflowRun)
        self.assertEqual(runs[0].id, "16679735137")
        self.assertEqual(runs[0].name, "CI")
    
    @patch('subprocess.run')
    def test_get_recent_runs_with_status_filter(self, mock_run):
        """Test retrieval with status filter"""
        mock_result = Mock()
        mock_result.stdout = json.dumps(get_sample_runs_data())
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        runs = self.manager.get_recent_runs(limit=5, status_filter="failure")
        
        # Verify status filter was passed to GitHub CLI
        call_args = mock_run.call_args[0][0]
        self.assertIn("--status", call_args)
        self.assertIn("failure", call_args)
    
    @patch('subprocess.run')
    def test_get_recent_runs_github_cli_error(self, mock_run):
        """Test handling of GitHub CLI errors"""
        # Mock GitHub CLI failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh run list")
        
        runs = self.manager.get_recent_runs()
        
        # Should return empty list on error
        self.assertEqual(runs, [])
    
    @patch('subprocess.run')
    def test_get_run_logs_success(self, mock_run):
        """Test successful log retrieval"""
        mock_result = Mock()
        mock_result.stdout = get_sample_log_npm_error()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        logs = self.manager.get_run_logs("12345")
        
        # Verify GitHub CLI was called correctly  
        call_args = mock_run.call_args[0][0]
        self.assertIn("gh", call_args)
        self.assertIn("run", call_args)
        self.assertIn("view", call_args)
        self.assertIn("12345", call_args)
        self.assertIn("--log", call_args)
        
        # Verify logs returned
        self.assertIn("npm ERR! code ENOENT", logs)
    
    def test_analyze_failure_patterns_npm_error(self):
        """Test pattern recognition for npm errors"""
        logs = get_sample_log_npm_error()
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Should detect npm package.json error
        self.assertGreater(len(patterns), 0)
        npm_patterns = [p for p in patterns if "npm" in p.pattern_name]
        self.assertGreater(len(npm_patterns), 0)
        
        npm_pattern = npm_patterns[0]
        self.assertEqual(npm_pattern.pattern_name, "npm_package_not_found")
        self.assertEqual(npm_pattern.confidence, 0.9)
        self.assertIn("ENOENT", npm_pattern.error_signature)
    
    def test_analyze_failure_patterns_python_import(self):
        """Test pattern recognition for Python import errors"""
        logs = get_sample_log_python_import_error()
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Should detect Python module missing error
        python_patterns = [p for p in patterns if "python" in p.pattern_name]
        self.assertGreater(len(python_patterns), 0)
        
        python_pattern = python_patterns[0]
        self.assertEqual(python_pattern.pattern_name, "python_module_missing")
        self.assertEqual(python_pattern.confidence, 0.85)
        self.assertIn("requests", python_pattern.error_signature)
    
    def test_analyze_failure_patterns_test_assertion(self):
        """Test pattern recognition for test assertion errors"""
        logs = get_sample_log_test_assertion_error()
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Should detect test assertion failure
        test_patterns = [p for p in patterns if "assertion" in p.pattern_name]
        self.assertGreater(len(test_patterns), 0)
        
        test_pattern = test_patterns[0]
        self.assertEqual(test_pattern.pattern_name, "test_failure_assertion")
        self.assertEqual(test_pattern.confidence, 0.7)
        self.assertIn("Expected 6 but got 5", test_pattern.error_signature)
    
    def test_analyze_failure_patterns_docker_error(self):
        """Test pattern recognition for Docker errors"""
        logs = get_sample_log_docker_error()
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Should detect Docker permission error
        docker_patterns = [p for p in patterns if "docker" in p.pattern_name]
        self.assertGreater(len(docker_patterns), 0)
        
        docker_pattern = docker_patterns[0]
        self.assertEqual(docker_pattern.pattern_name, "docker_permission_denied")
        self.assertEqual(docker_pattern.confidence, 0.85)
    
    def test_analyze_failure_patterns_cache_warning(self):
        """Test pattern recognition for cache warnings"""
        logs = get_sample_log_cache_warning()
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Should detect cache restore failure
        cache_patterns = [p for p in patterns if "cache" in p.pattern_name]
        self.assertGreater(len(cache_patterns), 0)
        
        cache_pattern = cache_patterns[0]
        self.assertEqual(cache_pattern.pattern_name, "cache_restore_failed")
        self.assertEqual(cache_pattern.confidence, 0.6)
    
    def test_analyze_failure_patterns_multiple_errors(self):
        """Test pattern recognition with multiple error types"""
        logs = get_sample_log_complex_multi_error()
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Should detect multiple patterns
        self.assertGreater(len(patterns), 1)
        
        pattern_names = [p.pattern_name for p in patterns]
        self.assertIn("npm_package_not_found", pattern_names)
        self.assertIn("python_module_missing", pattern_names) 
        self.assertIn("cache_restore_failed", pattern_names)
    
    def test_extract_file_context(self):
        """Test file context extraction"""
        logs = """
        Error in /path/to/file.js:25:10
        npm ERR! code ENOENT
        """
        
        # Find the error position
        error_pos = logs.find("npm ERR!")
        context = self.manager._extract_file_context(logs, error_pos)
        
        self.assertIsNotNone(context)
        self.assertIn("file.js", context)
    
    def test_extract_line_number(self):
        """Test line number extraction"""
        logs = """
        Error at line 25:10 in file.js
        npm ERR! code ENOENT
        """
        
        error_pos = logs.find("npm ERR!")
        line_num = self.manager._extract_line_number(logs, error_pos)
        
        self.assertEqual(line_num, 25)


class TestJobsStatusCommand(unittest.TestCase):
    """Test JobsStatusCommand functionality"""
    
    def setUp(self):
        self.command = JobsStatusCommand()
    
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_recent_runs')
    def test_execute_basic(self, mock_get_runs):
        """Test basic execution of jobs status command"""
        # Mock some failed runs
        sample_data = get_sample_runs_data()
        mock_runs = []
        for run_data in sample_data:
            run = WorkflowRun(
                id=str(run_data["databaseId"]),
                name=run_data["name"],
                status=run_data["status"], 
                conclusion=run_data["conclusion"],
                created_at=run_data["createdAt"],
                head_branch=run_data["headBranch"],
                event=run_data["event"],
                url=run_data.get("url", "")
            )
            mock_runs.append(run)
        
        mock_get_runs.return_value = mock_runs
        
        # Capture output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.command.execute(limit=3)
        
        output = mock_stdout.getvalue()
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["runs_found"], 0)
        self.assertIn("runs", result)
        
        # Verify output contains expected elements
        self.assertIn("GitHub Actions Failures", output)
        self.assertIn("CI", output)  # Should show CI workflow
    
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_recent_runs')
    def test_execute_with_branch_filter(self, mock_get_runs):
        """Test execution with branch filter"""
        sample_data = get_sample_runs_data()
        mock_runs = []
        for run_data in sample_data:
            run = WorkflowRun(
                id=str(run_data["databaseId"]),
                name=run_data["name"],
                status=run_data["status"],
                conclusion=run_data["conclusion"], 
                created_at=run_data["createdAt"],
                head_branch=run_data["headBranch"],
                event=run_data["event"],
                url=run_data.get("url", "")
            )
            mock_runs.append(run)
        
        mock_get_runs.return_value = mock_runs
        
        with patch('sys.stdout', new_callable=StringIO):
            result = self.command.execute(limit=5, branch="main")
        
        # Should only return runs from main branch
        for run in result["runs"]:
            # Only failed runs from main branch should be included
            if run["conclusion"] in ["failure", "cancelled"]:
                self.assertEqual(run["head_branch"], "main")
    
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_recent_runs')
    def test_execute_no_failures(self, mock_get_runs):
        """Test execution when no failures are found"""
        # Mock only successful runs
        success_run = WorkflowRun(
            id="12345", name="CI", status="completed", conclusion="success",
            created_at="2024-08-02T10:00:00Z", head_branch="main", event="push"
        )
        mock_get_runs.return_value = [success_run]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.command.execute()
        
        output = mock_stdout.getvalue()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["runs_found"], 0)
        self.assertIn("No recent failures found", output)
    
    def test_format_age(self):
        """Test age formatting"""
        # Test minutes
        age_str = self.command._format_age(0.5)  # 30 minutes
        self.assertIn("30 minutes ago", age_str)
        
        # Test hours
        age_str = self.command._format_age(2.5)  # 2.5 hours
        self.assertIn("2 hours ago", age_str)
        
        # Test days
        age_str = self.command._format_age(25)  # 25 hours = 1+ days
        self.assertIn("1 day ago", age_str)
        
        # Test multiple days
        age_str = self.command._format_age(50)  # 50 hours = 2+ days
        self.assertIn("2 days ago", age_str)


class TestJobsFailedInvestigateCommand(unittest.TestCase):
    """Test JobsFailedInvestigateCommand functionality"""
    
    def setUp(self):
        self.command = JobsFailedInvestigateCommand()
    
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_run_logs')
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_recent_runs')
    def test_execute_basic_investigation(self, mock_get_runs, mock_get_logs):
        """Test basic investigation execution"""
        # Mock failed runs
        failed_run = WorkflowRun(
            id="12345", name="CI", status="completed", conclusion="failure",
            created_at="2024-08-02T10:00:00Z", head_branch="main", event="push"
        )
        mock_get_runs.return_value = [failed_run]
        
        # Mock logs with npm error
        mock_get_logs.return_value = get_sample_log_npm_error()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.command.execute(runs_limit=1)
        
        output = mock_stdout.getvalue()
        
        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertIn("investigations", result)
        self.assertGreater(len(result["investigations"]), 0)
        
        # Verify investigation content
        investigation = result["investigations"][0]
        self.assertIn("patterns", investigation)
        self.assertIn("root_cause", investigation)
        self.assertIn("fix_recommendations", investigation)
        self.assertIn("confidence", investigation)
        
        # Verify output contains investigation report
        self.assertIn("Investigation Report", output)
        self.assertIn("Key Findings", output)
    
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_run_logs')
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_recent_runs')
    def test_investigate_run_with_patterns(self, mock_get_runs, mock_get_logs):
        """Test investigation of a run with detectable patterns"""
        failed_run = WorkflowRun(
            id="12345", name="CI", status="completed", conclusion="failure",
            created_at="2024-08-02T10:00:00Z", head_branch="main", event="push"
        )
        
        mock_get_logs.return_value = get_sample_log_npm_error()
        
        investigation = self.command._investigate_run(failed_run, confidence_threshold=0.5)
        
        # Verify investigation results
        self.assertIsInstance(investigation, InvestigationResult)
        self.assertEqual(investigation.run.id, "12345")
        self.assertGreater(len(investigation.patterns), 0)
        self.assertGreater(investigation.confidence, 0.5)
        
        # Verify npm pattern was detected
        npm_patterns = [p for p in investigation.patterns if "npm" in p.pattern_name]
        self.assertGreater(len(npm_patterns), 0)
    
    def test_determine_root_cause_single_pattern(self):
        """Test root cause determination with single pattern"""
        pattern = FailurePattern(
            pattern_name="npm_package_not_found",
            error_signature="npm ERR! code ENOENT",
            confidence=0.9,
            description="Missing package.json",
            suggested_fix="Check package.json location"
        )
        
        root_cause = self.command._determine_root_cause([pattern], "")
        self.assertEqual(root_cause, "Missing package.json")
    
    def test_determine_root_cause_multiple_patterns(self):
        """Test root cause determination with multiple patterns"""
        patterns = [
            FailurePattern(
                pattern_name="npm_package_not_found", error_signature="npm ERR!", 
                confidence=0.9, description="Missing package.json", suggested_fix="Fix npm"
            ),
            FailurePattern(
                pattern_name="cache_restore_failed", error_signature="cache failed",
                confidence=0.6, description="Cache issue", suggested_fix="Fix cache"
            )
        ]
        
        root_cause = self.command._determine_root_cause(patterns, "")
        self.assertIn("Missing package.json", root_cause)
        self.assertIn("1 related issues", root_cause)
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        patterns = [
            FailurePattern(
                pattern_name="npm_package_not_found", error_signature="npm ERR!",
                confidence=0.9, description="Missing package.json", 
                suggested_fix="Check package.json location"
            )
        ]
        
        recommendations = self.command._generate_recommendations(patterns)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("package.json" in rec for rec in recommendations))
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation"""
        patterns = [
            FailurePattern("test1", "error1", 0.9, "desc1", "fix1"),
            FailurePattern("test2", "error2", 0.7, "desc2", "fix2")
        ]
        
        confidence = self.command._calculate_overall_confidence(patterns)
        self.assertGreater(confidence, 0.7)
        self.assertLessEqual(confidence, 0.95)
    
    @patch('gha_jobs_commands.GitHubActionsJobsManager.get_recent_runs')
    def test_execute_no_failures(self, mock_get_runs):
        """Test execution when no failures found"""
        mock_get_runs.return_value = []
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.command.execute()
        
        output = mock_stdout.getvalue()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["investigations"]), 0)
        self.assertIn("No recent failures", output)


class TestJobsFixFailedNGUCommand(unittest.TestCase):
    """Test JobsFixFailedNGUCommand functionality"""
    
    def setUp(self):
        self.command = JobsFixFailedNGUCommand()
    
    def test_execute_demo_mode(self):
        """Test NGU command execution in demo mode"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.command.execute()
        
        output = mock_stdout.getvalue()
        
        # Verify demo mode output
        self.assertEqual(result["status"], "demo")
        self.assertIn("NGU MODE ACTIVATED", output)
        self.assertIn("Never Give Up", output)
        self.assertIn("demonstration", output)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for common usage scenarios"""
    
    def setUp(self):
        self.manager = GitHubActionsJobsManager()
        self.status_cmd = JobsStatusCommand()
        self.investigate_cmd = JobsFailedInvestigateCommand()
    
    @patch('subprocess.run')
    def test_full_workflow_status_to_investigation(self, mock_run):
        """Test full workflow from status check to investigation"""
        # Mock GitHub CLI responses
        runs_response = Mock()
        runs_response.stdout = json.dumps(get_sample_runs_data())
        runs_response.returncode = 0
        
        logs_response = Mock()
        logs_response.stdout = get_sample_log_npm_error()
        logs_response.returncode = 0
        
        # Set up mock to return different responses for different calls
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                return runs_response
            elif "view" in cmd and "--log" in cmd:
                return logs_response
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        # Execute status command
        with patch('sys.stdout', new_callable=StringIO):
            status_result = self.status_cmd.execute(limit=3)
        
        # Verify we found failures
        self.assertGreater(status_result["runs_found"], 0)
        
        # Execute investigation on the failures
        with patch('sys.stdout', new_callable=StringIO):
            investigate_result = self.investigate_cmd.execute(runs_limit=2)
        
        # Verify investigation completed
        self.assertEqual(investigate_result["status"], "success")
        self.assertGreater(len(investigate_result["investigations"]), 0)
        
        # Verify pattern detection worked
        investigation = investigate_result["investigations"][0]
        self.assertGreater(len(investigation["patterns"]), 0)


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestWorkflowRun,
        TestGitHubActionsJobsManager, 
        TestJobsStatusCommand,
        TestJobsFailedInvestigateCommand,
        TestJobsFixFailedNGUCommand,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)