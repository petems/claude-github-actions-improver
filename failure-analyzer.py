#!/usr/bin/env python3
"""
GitHub Actions Failure Analyzer

Analyzes actual workflow run failures and provides intelligent fixes
based on error patterns, logs, and common failure scenarios.
"""

import json
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

class GitHubActionsFailureAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        
    def get_recent_workflow_runs(self, limit: int = 20) -> List[Dict]:
        """Get recent workflow runs using GitHub CLI."""
        try:
            cmd = [
                "gh", "run", "list", 
                "--limit", str(limit),
                "--json", "databaseId,name,status,conclusion,createdAt,headBranch,event,workflowName,url"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"⚠️  GitHub CLI error: {result.stderr}")
                return []
        except Exception as e:
            print(f"⚠️  Could not fetch workflow runs: {e}")
            return []
    
    def get_failed_runs(self, runs: List[Dict]) -> List[Dict]:
        """Filter for failed workflow runs."""
        failed_runs = []
        for run in runs:
            if run.get("conclusion") == "failure":
                failed_runs.append(run)
        return failed_runs
    
    def get_run_logs(self, run_id: str) -> str:
        """Get detailed logs for a specific workflow run."""
        try:
            cmd = ["gh", "run", "view", run_id, "--log"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
        except Exception as e:
            print(f"⚠️  Could not fetch logs for run {run_id}: {e}")
            return ""
    
    def get_run_jobs(self, run_id: str) -> List[Dict]:
        """Get job details for a specific workflow run."""
        try:
            cmd = [
                "gh", "run", "view", run_id,
                "--json", "jobs"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("jobs", [])
            else:
                return []
        except Exception as e:
            print(f"⚠️  Could not fetch jobs for run {run_id}: {e}")
            return []
    
    def analyze_failure_patterns(self, logs: str, job_name: str = "") -> Dict:
        """Analyze logs to identify failure patterns and suggest fixes."""
        failure_analysis = {
            "error_type": "unknown",
            "error_message": "",
            "suggested_fixes": [],
            "confidence": 0.0,
            "workflow_changes": [],
            "code_changes": []
        }
        
        # Common failure patterns with their fixes
        failure_patterns = [
            # Node.js/npm failures
            {
                "pattern": r"npm ERR!.*ENOENT.*package\.json",
                "error_type": "missing_package_json",
                "message": "package.json not found",
                "fixes": [
                    "Add package.json file to repository root",
                    "Update workflow to run from correct directory with package.json"
                ],
                "workflow_changes": [
                    "Add 'working-directory' parameter to npm steps",
                    "Add step to verify package.json exists before npm install"
                ],
                "confidence": 0.9
            },
            {
                "pattern": r"npm ERR!.*404.*not found",
                "error_type": "npm_package_not_found",
                "message": "npm package not found",
                "fixes": [
                    "Check package names in package.json for typos",
                    "Verify package exists on npm registry",
                    "Update to correct package version"
                ],
                "confidence": 0.8
            },
            {
                "pattern": r"npm ERR!.*peer dep.*ERESOLVE",
                "error_type": "npm_peer_dependency",
                "message": "npm peer dependency conflict",
                "fixes": [
                    "Use 'npm install --legacy-peer-deps' in workflow",
                    "Update package.json to resolve peer dependency conflicts",
                    "Use npm ci with --force flag"
                ],
                "workflow_changes": [
                    "Replace 'npm ci' with 'npm ci --legacy-peer-deps'",
                    "Add npm config set legacy-peer-deps true"
                ],
                "confidence": 0.9
            },
            
            # Python failures
            {
                "pattern": r"ERROR:.*No module named '(\w+)'",
                "error_type": "python_missing_module",
                "message": "Python module not found",
                "fixes": [
                    "Add missing module to requirements.txt",
                    "Install module in workflow before tests",
                    "Check if module name is correct"
                ],
                "workflow_changes": [
                    "Add missing dependencies to requirements.txt installation",
                    "Add explicit pip install step for missing modules"
                ],
                "confidence": 0.9
            },
            {
                "pattern": r"SyntaxError:|IndentationError:",
                "error_type": "python_syntax_error",
                "message": "Python syntax or indentation error",
                "fixes": [
                    "Fix syntax errors in Python code",
                    "Check indentation consistency",
                    "Run local linting before committing"
                ],
                "code_changes": [
                    "Fix syntax errors identified in logs",
                    "Run flake8 or black formatter"
                ],
                "confidence": 0.95
            },
            {
                "pattern": r"ImportError:.*cannot import name",
                "error_type": "python_import_error",
                "message": "Python import error",
                "fixes": [
                    "Check import paths and module structure",
                    "Verify __init__.py files exist",
                    "Update imports to correct module paths"
                ],
                "confidence": 0.8
            },
            
            # Testing failures
            {
                "pattern": r"FAILED.*test_.*\.py::\w+",
                "error_type": "test_failure",
                "message": "Unit tests failing",
                "fixes": [
                    "Fix failing test assertions",
                    "Update test data or mocks",
                    "Check if code changes broke expected behavior"
                ],
                "code_changes": [
                    "Analyze failing test output and fix underlying issues",
                    "Update test expectations if behavior change is intentional"
                ],
                "confidence": 0.7
            },
            
            # Build/compilation failures
            {
                "pattern": r"error: (.+)\n.*--> (.+):(\d+):(\d+)",
                "error_type": "rust_compile_error",
                "message": "Rust compilation error",
                "fixes": [
                    "Fix Rust compilation errors in source code",
                    "Update Rust dependencies if needed",
                    "Check Rust toolchain version compatibility"
                ],
                "confidence": 0.9
            },
            {
                "pattern": r"go: (.+@.+): (.+)",
                "error_type": "go_module_error",
                "message": "Go module error",
                "fixes": [
                    "Run 'go mod tidy' to clean up dependencies",
                    "Update go.mod with correct module versions",
                    "Check if module exists and is accessible"
                ],
                "workflow_changes": [
                    "Add 'go mod download' step before build",
                    "Add 'go mod tidy' step to verify dependencies"
                ],
                "confidence": 0.8
            },
            
            # Docker/container failures
            {
                "pattern": r"docker: Error response from daemon:",
                "error_type": "docker_error",
                "message": "Docker container error",
                "fixes": [
                    "Check Docker image availability",
                    "Verify Dockerfile syntax",
                    "Check container resource requirements"
                ],
                "confidence": 0.7
            },
            
            # Environment/setup failures
            {
                "pattern": r"ERROR: The request is invalid: (.+)",
                "error_type": "github_api_error",
                "message": "GitHub API or permissions error",
                "fixes": [
                    "Check GITHUB_TOKEN permissions",
                    "Verify repository access settings",
                    "Update workflow permissions section"
                ],
                "workflow_changes": [
                    "Add appropriate permissions to workflow",
                    "Check if GITHUB_TOKEN needs additional scopes"
                ],
                "confidence": 0.8
            },
            
            # Cache failures
            {
                "pattern": r"Warning: Failed to restore cache",
                "error_type": "cache_failure",
                "message": "Cache restore failed",
                "fixes": [
                    "Update cache key patterns",
                    "Clear old cache if corrupted",
                    "Add fallback cache keys"
                ],
                "workflow_changes": [
                    "Update cache action with better key patterns",
                    "Add restore-keys for cache fallbacks"
                ],
                "confidence": 0.6
            }
        ]
        
        # Analyze logs for patterns
        for pattern_info in failure_patterns:
            matches = re.findall(pattern_info["pattern"], logs, re.MULTILINE | re.IGNORECASE)
            if matches:
                failure_analysis["error_type"] = pattern_info["error_type"]
                failure_analysis["error_message"] = pattern_info["message"]
                failure_analysis["suggested_fixes"] = pattern_info["fixes"]
                failure_analysis["confidence"] = pattern_info["confidence"]
                failure_analysis["workflow_changes"] = pattern_info.get("workflow_changes", [])
                failure_analysis["code_changes"] = pattern_info.get("code_changes", [])
                
                # Extract specific error details from matches
                if matches and isinstance(matches[0], tuple):
                    failure_analysis["error_details"] = matches[0]
                elif matches:
                    failure_analysis["error_details"] = matches[0]
                
                break
        
        return failure_analysis
    
    def generate_fix_suggestions(self, run_analysis: Dict) -> str:
        """Generate comprehensive fix suggestions for a failed run."""
        suggestions = []
        
        suggestions.append(f"## 🔍 Failure Analysis: {run_analysis['workflow_name']}")
        suggestions.append(f"**Run ID:** {run_analysis['run_id']}")
        suggestions.append(f"**Failed Jobs:** {', '.join(run_analysis['failed_jobs'])}")
        suggestions.append("")
        
        for job_name, analysis in run_analysis['job_analyses'].items():
            if analysis['error_type'] != 'unknown':
                suggestions.append(f"### 🔨 {job_name}")
                suggestions.append(f"**Error Type:** {analysis['error_type']}")
                suggestions.append(f"**Issue:** {analysis['error_message']}")
                suggestions.append(f"**Confidence:** {analysis['confidence']:.0%}")
                suggestions.append("")
                
                if analysis['suggested_fixes']:
                    suggestions.append("**Recommended Fixes:**")
                    for fix in analysis['suggested_fixes']:
                        suggestions.append(f"- {fix}")
                    suggestions.append("")
                
                if analysis['workflow_changes']:
                    suggestions.append("**Workflow Changes:**")
                    for change in analysis['workflow_changes']:
                        suggestions.append(f"- {change}")
                    suggestions.append("")
                
                if analysis['code_changes']:
                    suggestions.append("**Code Changes:**")
                    for change in analysis['code_changes']:
                        suggestions.append(f"- {change}")
                    suggestions.append("")
        
        return "\n".join(suggestions)
    
    def analyze_recent_failures(self, days_back: int = 7, max_runs: int = 10) -> List[Dict]:
        """Analyze recent workflow failures and provide fix suggestions."""
        print("🔍 Fetching recent workflow runs...")
        runs = self.get_recent_workflow_runs(limit=50)
        
        if not runs:
            print("❌ No workflow runs found. Make sure you're in a repository with GitHub Actions.")
            return []
        
        # Filter for recent failed runs
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_failed_runs = []
        
        for run in runs:
            if run.get("conclusion") == "failure":
                run_date = datetime.fromisoformat(run["createdAt"].replace('Z', '+00:00'))
                if run_date >= cutoff_date:
                    recent_failed_runs.append(run)
        
        if not recent_failed_runs:
            print("✅ No recent failed workflow runs found!")
            return []
        
        print(f"🔨 Analyzing {min(len(recent_failed_runs), max_runs)} recent failures...")
        
        analyses = []
        for run in recent_failed_runs[:max_runs]:
            print(f"📋 Analyzing run: {run['workflowName']} ({run['databaseId']})")
            
            # Get detailed job information
            jobs = self.get_run_jobs(str(run['databaseId']))
            failed_jobs = [job for job in jobs if job.get('conclusion') == 'failure']
            
            if not failed_jobs:
                continue
            
            run_analysis = {
                'run_id': run['databaseId'],
                'workflow_name': run['workflowName'],
                'url': run['url'],
                'created_at': run['createdAt'],
                'failed_jobs': [job['name'] for job in failed_jobs],
                'job_analyses': {}
            }
            
            # Analyze each failed job
            for job in failed_jobs:
                print(f"  🔍 Analyzing job: {job['name']}")
                
                # Get logs for this specific run
                logs = self.get_run_logs(str(run['databaseId']))
                
                # Analyze failure patterns
                analysis = self.analyze_failure_patterns(logs, job['name'])
                run_analysis['job_analyses'][job['name']] = analysis
            
            analyses.append(run_analysis)
        
        return analyses

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze GitHub Actions failures")
    parser.add_argument("--days", type=int, default=7, help="Days back to analyze (default: 7)")
    parser.add_argument("--max-runs", type=int, default=10, help="Max runs to analyze (default: 10)")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    analyzer = GitHubActionsFailureAnalyzer(args.repo_path)
    analyses = analyzer.analyze_recent_failures(args.days, args.max_runs)
    
    if analyses:
        print(f"\n🎯 Analysis Results ({len(analyses)} failed runs)")
        print("=" * 50)
        
        for analysis in analyses:
            suggestions = analyzer.generate_fix_suggestions(analysis)
            print(suggestions)
            print("-" * 50)
    else:
        print("\n✅ No recent failures to analyze!")

if __name__ == "__main__":
    main()