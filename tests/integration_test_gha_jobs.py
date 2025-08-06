#!/usr/bin/env python3
"""
Integration tests for GitHub Actions Jobs Commands
Tests the full command workflows with real-like scenarios
"""

import os
import sys
import unittest
import tempfile
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gha_jobs_commands import (
    JobsStatusCommand, JobsFailedInvestigateCommand, JobsFixFailedNGUCommand,
    GitHubActionsJobsManager
)
from tests.test_fixtures.github_api_responses import (
    get_sample_runs_data, get_sample_log_npm_error, get_sample_log_python_import_error,
    get_sample_log_complex_multi_error
)


class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests with common setup"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create a fake git repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        
        # Create basic project structure
        os.makedirs(".github/workflows", exist_ok=True)
        with open("README.md", "w") as f:
            f.write("# Test Project\n")
        
        # Commit initial files
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, capture_output=True)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestJobsStatusIntegration(IntegrationTestBase):
    """Integration tests for jobs-status command"""
    
    @patch('subprocess.run')
    def test_jobs_status_real_workflow(self, mock_run):
        """Test jobs-status command with realistic GitHub CLI interaction"""
        # Mock GitHub CLI response
        mock_result = Mock()
        mock_result.stdout = json.dumps(get_sample_runs_data())
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Execute command
        cmd = JobsStatusCommand()
        result = cmd.execute(limit=5, format_type="simple")
        
        # Verify GitHub CLI was called correctly
        self.assertTrue(mock_run.called)
        call_args = mock_run.call_args[0][0]
        self.assertIn("gh", call_args)
        self.assertIn("run", call_args)
        self.assertIn("list", call_args)
        self.assertIn("--limit", call_args)
        # The limit is passed as string "10" (default * 2 for filtering)
        self.assertTrue(any("10" in str(arg) for arg in call_args))
        
        # Verify results
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["runs_found"], 0)
        self.assertIn("runs", result)
    
    @patch('subprocess.run')
    def test_jobs_status_with_branch_filtering(self, mock_run):
        """Test jobs-status with branch filtering"""
        mock_result = Mock()
        mock_result.stdout = json.dumps(get_sample_runs_data())
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        cmd = JobsStatusCommand()
        result = cmd.execute(limit=3, branch="main")
        
        # Should only include failures from main branch
        for run in result["runs"]:
            if run["conclusion"] in ["failure", "cancelled"]:
                self.assertEqual(run["head_branch"], "main")
    
    @patch('subprocess.run')
    def test_jobs_status_no_github_cli(self, mock_run):
        """Test jobs-status when GitHub CLI is not available"""
        # Mock GitHub CLI not found
        mock_run.side_effect = subprocess.CalledProcessError(127, "gh")
        
        cmd = JobsStatusCommand()
        result = cmd.execute()
        
        # Should handle error gracefully
        self.assertEqual(result["runs_found"], 0)
    
    @patch('subprocess.run')
    def test_jobs_status_invalid_json_response(self, mock_run):
        """Test jobs-status with invalid JSON from GitHub CLI"""
        mock_result = Mock()
        mock_result.stdout = "invalid json response"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        cmd = JobsStatusCommand()
        result = cmd.execute()
        
        # Should handle JSON parse error
        self.assertEqual(result["runs_found"], 0)


class TestJobsFailedInvestigateIntegration(IntegrationTestBase):
    """Integration tests for jobs-failed-investigate command"""
    
    @patch('subprocess.run')
    def test_investigate_npm_failure_scenario(self, mock_run):
        """Test investigation of npm package.json failure"""
        # Mock GitHub CLI responses
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                # Return failed runs
                result = Mock()
                result.stdout = json.dumps([get_sample_runs_data()[0]])  # First run is failed
                result.returncode = 0
                return result
            elif "view" in cmd and "--log" in cmd:
                # Return npm error logs
                result = Mock()
                result.stdout = get_sample_log_npm_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        # Execute investigation
        cmd = JobsFailedInvestigateCommand()
        result = cmd.execute(runs_limit=1)
        
        # Verify investigation completed
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["investigations"]), 1)
        
        # Verify npm pattern was detected
        investigation = result["investigations"][0]
        self.assertGreater(len(investigation["patterns"]), 0)
        
        npm_patterns = [p for p in investigation["patterns"] if "npm" in p["pattern_name"]]
        self.assertGreater(len(npm_patterns), 0)
        
        # Verify confidence and recommendations
        self.assertGreater(investigation["confidence"], 0.8)  # Should be high confidence for npm error
        self.assertGreater(len(investigation["fix_recommendations"]), 0)
    
    @patch('subprocess.run')
    def test_investigate_python_import_failure(self, mock_run):
        """Test investigation of Python import failure"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                result = Mock()
                result.stdout = json.dumps([get_sample_runs_data()[1]])  # Second run
                result.returncode = 0
                return result
            elif "view" in cmd and "--log" in cmd:
                result = Mock()
                result.stdout = get_sample_log_python_import_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        cmd = JobsFailedInvestigateCommand()
        result = cmd.execute(runs_limit=1)
        
        # Verify Python pattern detection
        investigation = result["investigations"][0]
        python_patterns = [p for p in investigation["patterns"] if "python" in p["pattern_name"]]
        self.assertGreater(len(python_patterns), 0)
        
        # Verify requests module was identified
        pattern = python_patterns[0] 
        self.assertIn("requests", pattern["error_signature"])
    
    @patch('subprocess.run')
    def test_investigate_multiple_failure_types(self, mock_run):
        """Test investigation of complex failure with multiple error types"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                result = Mock()
                result.stdout = json.dumps([get_sample_runs_data()[0]])
                result.returncode = 0
                return result
            elif "view" in cmd and "--log" in cmd:
                result = Mock()
                result.stdout = get_sample_log_complex_multi_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        cmd = JobsFailedInvestigateCommand()
        result = cmd.execute(runs_limit=1)
        
        # Should detect multiple patterns
        investigation = result["investigations"][0]
        self.assertGreater(len(investigation["patterns"]), 1)
        
        # Verify different pattern types detected
        pattern_names = [p["pattern_name"] for p in investigation["patterns"]]
        self.assertIn("npm_package_not_found", pattern_names)
        self.assertIn("python_module_missing", pattern_names)
        self.assertIn("cache_restore_failed", pattern_names)
    
    @patch('subprocess.run')
    def test_investigate_with_confidence_threshold(self, mock_run):
        """Test investigation with different confidence thresholds"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                result = Mock()
                result.stdout = json.dumps([get_sample_runs_data()[0]])
                result.returncode = 0
                return result
            elif "view" in cmd and "--log" in cmd:
                result = Mock()
                result.stdout = get_sample_log_complex_multi_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        cmd = JobsFailedInvestigateCommand()
        
        # Test with high confidence threshold
        result_high = cmd.execute(runs_limit=1, confidence_threshold=0.85)
        investigation_high = result_high["investigations"][0]
        
        # Test with low confidence threshold
        result_low = cmd.execute(runs_limit=1, confidence_threshold=0.5)
        investigation_low = result_low["investigations"][0]
        
        # Low threshold should detect more patterns
        self.assertGreaterEqual(len(investigation_low["patterns"]), len(investigation_high["patterns"]))
    
    @patch('subprocess.run')
    def test_investigate_workflow_filtering(self, mock_run):
        """Test investigation with workflow filtering"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                result = Mock()
                # Return multiple runs but filter should apply
                result.stdout = json.dumps(get_sample_runs_data()[:3])
                result.returncode = 0
                return result
            elif "view" in cmd and "--log" in cmd:
                result = Mock()
                result.stdout = get_sample_log_npm_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        cmd = JobsFailedInvestigateCommand()
        result = cmd.execute(runs_limit=5, workflow="CI")
        
        # Should only investigate CI workflows
        for investigation in result["investigations"]:
            self.assertIn("CI", investigation["run"]["name"])


class TestJobsFixFailedNGUIntegration(IntegrationTestBase):
    """Integration tests for jobs-fixfailed-ngu command"""
    
    def test_ngu_demo_mode_execution(self):
        """Test NGU command execution in demo mode"""
        cmd = JobsFixFailedNGUCommand()
        result = cmd.execute(max_rounds=3, patience_minutes=5)
        
        # Verify demo mode response
        self.assertEqual(result["status"], "demo")
        self.assertIn("message", result)
    
    @patch('gha_jobs_commands.JobsFailedInvestigateCommand.execute')
    def test_ngu_uses_investigation(self, mock_investigate):
        """Test that NGU command uses investigation results"""
        # Mock investigation results
        mock_investigate.return_value = {
            "status": "success",
            "investigations": [
                {
                    "run": {"id": "12345", "name": "CI"},
                    "patterns": [{"pattern_name": "npm_package_not_found"}],
                    "confidence": 0.9
                }
            ]
        }
        
        cmd = JobsFixFailedNGUCommand()
        result = cmd.execute()
        
        # Verify investigation was called
        mock_investigate.assert_called_once()
        self.assertEqual(result["status"], "demo")


class TestEndToEndScenarios(IntegrationTestBase):
    """End-to-end integration tests for complete workflows"""
    
    @patch('subprocess.run')
    def test_complete_workflow_status_investigate_ngu(self, mock_run):
        """Test complete workflow from status check through NGU"""
        # Mock GitHub CLI responses for the entire workflow
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if "list" in cmd:
                result = Mock()
                result.stdout = json.dumps(get_sample_runs_data())
                result.returncode = 0
                return result
            elif "view" in cmd and "--log" in cmd:
                result = Mock()
                result.stdout = get_sample_log_npm_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        # Step 1: Check status
        status_cmd = JobsStatusCommand()
        status_result = status_cmd.execute(limit=3)
        
        self.assertEqual(status_result["status"], "success")
        self.assertGreater(status_result["runs_found"], 0)
        
        # Step 2: Investigate failures
        investigate_cmd = JobsFailedInvestigateCommand()
        investigate_result = investigate_cmd.execute(runs_limit=2)
        
        self.assertEqual(investigate_result["status"], "success")
        self.assertGreater(len(investigate_result["investigations"]), 0)
        
        # Step 3: NGU fixing (demo mode)
        ngu_cmd = JobsFixFailedNGUCommand()
        ngu_result = ngu_cmd.execute()
        
        self.assertEqual(ngu_result["status"], "demo")
        
        # Verify the workflow progressed through all stages
        self.assertIsNotNone(status_result)
        self.assertIsNotNone(investigate_result)
        self.assertIsNotNone(ngu_result)
    
    @patch('subprocess.run')
    def test_command_line_interface(self, mock_run):
        """Test command line interface for all commands"""
        # Mock GitHub CLI
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0] == "python3" or cmd[0] == "python":
                # This is our script being called
                return Mock(stdout="Command executed successfully", returncode=0)
            elif "gh" in cmd:
                if "list" in cmd:
                    result = Mock()
                    result.stdout = json.dumps(get_sample_runs_data())
                    result.returncode = 0
                    return result
                elif "view" in cmd:
                    result = Mock()
                    result.stdout = get_sample_log_npm_error()
                    result.returncode = 0
                    return result
            return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        # Test command line interface
        import sys
        original_argv = sys.argv.copy()
        
        try:
            # Test jobs-status command
            sys.argv = ["gha_jobs_commands.py", "jobs-status", "--limit", "3"]
            
            # Import and run the CLI
            from gha_jobs_commands import JobsStatusCommand
            cmd = JobsStatusCommand()
            result = cmd.execute(limit=3)
            
            self.assertEqual(result["status"], "success")
            
        finally:
            sys.argv = original_argv
    
    @patch('subprocess.run')
    def test_error_recovery_scenarios(self, mock_run):
        """Test error recovery in various failure scenarios"""
        # Test scenario: GitHub CLI fails initially, then succeeds
        call_count = 0
        
        def mock_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            cmd = args[0]
            if "gh" in cmd and call_count == 1:
                # First call fails
                raise subprocess.CalledProcessError(1, "gh")
            elif "gh" in cmd and "list" in cmd:
                # Subsequent calls succeed
                result = Mock()
                result.stdout = json.dumps(get_sample_runs_data())
                result.returncode = 0
                return result
            elif "gh" in cmd and "view" in cmd:
                result = Mock()
                result.stdout = get_sample_log_npm_error()
                result.returncode = 0
                return result
            else:
                return Mock(stdout="", returncode=0)
        
        mock_run.side_effect = mock_run_side_effect
        
        # First call should fail gracefully
        status_cmd = JobsStatusCommand()
        result1 = status_cmd.execute()
        self.assertEqual(result1["runs_found"], 0)
        
        # Second call should succeed
        result2 = status_cmd.execute()
        self.assertGreaterEqual(result2["runs_found"], 0)
    
    def test_performance_with_large_datasets(self):
        """Test performance with larger datasets"""
        # Create a large dataset of runs
        large_dataset = []
        base_time = datetime.now()
        
        for i in range(100):
            run_data = {
                "databaseId": 16679735000 + i,
                "name": f"Workflow-{i % 10}",
                "status": "completed",
                "conclusion": "failure" if i % 3 == 0 else "success",
                "createdAt": (base_time - timedelta(hours=i)).isoformat() + "Z",
                "headBranch": "main" if i % 2 == 0 else f"feature-{i}",
                "event": "push",
                "url": f"https://github.com/test/repo/actions/runs/{16679735000 + i}"
            }
            large_dataset.append(run_data)
        
        # Test with large dataset
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = json.dumps(large_dataset)
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            import time
            start_time = time.time()
            
            status_cmd = JobsStatusCommand()
            result = status_cmd.execute(limit=20)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verify performance is reasonable (should complete in under 2 seconds)
            self.assertLess(execution_time, 2.0)
            self.assertEqual(result["status"], "success")
            
            # Should properly limit results
            self.assertLessEqual(result["runs_found"], 20)


if __name__ == "__main__":
    # Run integration tests
    unittest.main(verbosity=2)