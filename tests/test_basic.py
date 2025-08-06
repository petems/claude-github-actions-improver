#!/usr/bin/env python3
"""
Basic tests for GitHub Actions Improver
Ensures the test infrastructure is working correctly
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests"""
    
    def test_python_environment(self):
        """Test that Python environment is working"""
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 9)
    
    def test_project_structure(self):
        """Test that required project files exist"""
        project_files = [
            "requirements.txt",
            "failure-analyzer.py",
            "github-actions-improver-minimal.py",
            "claude-agent-github-actions-enhanced.py",
            "wgu-fighter.py"
        ]
        
        for file_name in project_files:
            file_path = project_root / file_name
            self.assertTrue(file_path.exists(), f"Missing required file: {file_name}")
    
    def test_workflows_exist(self):
        """Test that GitHub workflows exist"""
        workflows_dir = project_root / ".github" / "workflows"
        self.assertTrue(workflows_dir.exists(), "Workflows directory missing")
        
        workflow_files = list(workflows_dir.glob("*.yml"))
        self.assertGreater(len(workflow_files), 0, "No workflow files found")
    
    def test_basic_imports(self):
        """Test that basic Python imports work"""
        try:
            import json
            import subprocess
            import pathlib
            import concurrent.futures
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")


class TestToolFunctionality(unittest.TestCase):
    """Test the actual tool functionality"""
    
    def test_failure_analyzer_exists(self):
        """Test that failure analyzer script exists and is executable"""
        analyzer_path = project_root / "failure-analyzer.py"
        self.assertTrue(analyzer_path.exists())
        self.assertTrue(os.access(analyzer_path, os.X_OK))
    
    def test_wgu_fighter_exists(self):
        """Test that WGU fighter script exists and is executable"""
        wgu_path = project_root / "wgu-fighter.py"
        self.assertTrue(wgu_path.exists())
        self.assertTrue(os.access(wgu_path, os.X_OK))
    
    def test_requirements_parseable(self):
        """Test that requirements.txt is valid"""
        requirements_path = project_root / "requirements.txt"
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                content = f.read()
                self.assertIsInstance(content, str)
                # Should contain some basic requirements
                self.assertIn("python", content.lower())


if __name__ == "__main__":
    unittest.main()