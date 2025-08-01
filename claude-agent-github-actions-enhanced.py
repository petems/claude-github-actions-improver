#!/usr/bin/env python3
"""
Claude Agent: GitHub Actions Improver - Enhanced with Real Failure Analysis

This enhanced version analyzes actual workflow run failures from GitHub Actions logs
and provides intelligent fixes based on error patterns and common failure scenarios.
"""

import os
import sys
import subprocess
import json
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional

class EnhancedGitHubActionsAgent:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        
        # Import failure analyzer
        sys.path.append(str(Path(__file__).parent))
        try:
            from failure_analyzer import GitHubActionsFailureAnalyzer
            self.failure_analyzer = GitHubActionsFailureAnalyzer(str(self.repo_path))
        except ImportError:
            print("⚠️  Failure analyzer not available")
            self.failure_analyzer = None
        
    def detect_project_info(self) -> Dict[str, any]:
        """Detect comprehensive project information."""
        info = {
            "type": "generic",
            "languages": [],
            "frameworks": [],
            "has_tests": False,
            "has_workflows": False,
            "project_files": []
        }
        
        # Language detection
        project_indicators = {
            'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', '*.py'],
            'node': ['package.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'rust': ['Cargo.toml'],
            'go': ['go.mod', 'go.sum'],
            'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
            'php': ['composer.json'],
            'ruby': ['Gemfile', 'Rakefile'],
            'dotnet': ['*.csproj', '*.sln'],
            'docker': ['Dockerfile', 'docker-compose.yml']
        }
        
        for lang, indicators in project_indicators.items():
            for indicator in indicators:
                if list(self.repo_path.glob(indicator)):
                    info["languages"].append(lang)
                    info["project_files"].extend([str(f) for f in self.repo_path.glob(indicator)])
                    break
        
        # Primary type
        if 'python' in info["languages"]:
            info["type"] = "python"
        elif 'node' in info["languages"]:
            info["type"] = "node"
        elif info["languages"]:
            info["type"] = info["languages"][0]
        
        # Test detection
        test_patterns = ['**/test*.py', '**/test*.js', '**/test*.go', '**/test*.rs', 
                        '**/tests/**', '**/spec/**', '**/__tests__/**']
        for pattern in test_patterns:
            if list(self.repo_path.glob(pattern)):
                info["has_tests"] = True
                break
        
        # Workflow detection
        info["has_workflows"] = self.has_workflows()
        
        return info
    
    def has_workflows(self) -> bool:
        """Check if repository has GitHub Actions workflows."""
        if not self.workflows_dir.exists():
            return False
        return any(self.workflows_dir.glob("*.yml")) or any(self.workflows_dir.glob("*.yaml"))
    
    def get_workflow_files(self) -> List[Path]:
        """Get all workflow files."""
        if not self.workflows_dir.exists():
            return []
        workflows = []
        workflows.extend(self.workflows_dir.glob("*.yml"))
        workflows.extend(self.workflows_dir.glob("*.yaml"))
        return workflows
    
    def run_claude_subprocess(self, prompt: str, task_name: str = "") -> str:
        """Run Claude CLI in subprocess with optimized prompt."""
        cmd = ["claude", "--print", prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=self.repo_path, timeout=60)
            if result.returncode != 0:
                print(f"❌ Claude error for {task_name}: {result.stderr}")
                return ""
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"⏰ Claude timeout for {task_name}")
            return ""
        except Exception as e:
            print(f"❌ Error running Claude for {task_name}: {e}")
            return ""
    
    def extract_yaml_content(self, response: str) -> str:
        """Extract YAML from Claude response."""
        if "```yaml" in response:
            return response.split("```yaml")[1].split("```")[0].strip()
        elif "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if "name:" in part and ("on:" in part or "jobs:" in part):
                    return part.strip()
        return response.strip()
    
    def analyze_real_failures(self) -> List[Dict]:
        """Analyze real workflow failures using GitHub Actions API."""
        if not self.failure_analyzer:
            print("⚠️  GitHub CLI not available for failure analysis")
            return []
        
        print("🔍 Analyzing recent workflow failures...")
        try:
            failure_analyses = self.failure_analyzer.analyze_recent_failures(days_back=14, max_runs=10)
            return failure_analyses
        except Exception as e:
            print(f"⚠️  Could not analyze failures: {e}")
            return []
    
    def fix_workflow_with_failure_context(self, workflow_file: Path, failure_analysis: Dict) -> Dict:
        """Fix workflow based on actual failure analysis."""
        try:
            with open(workflow_file, 'r') as f:
                current_content = f.read()
            
            # Build context-aware prompt based on failure analysis
            failure_context = ""
            if failure_analysis.get('job_analyses'):
                failure_context = "Recent failure analysis:\n"
                for job_name, analysis in failure_analysis['job_analyses'].items():
                    if analysis['error_type'] != 'unknown':
                        failure_context += f"- Job '{job_name}': {analysis['error_message']}\n"
                        failure_context += f"  Error type: {analysis['error_type']}\n"
                        if analysis['suggested_fixes']:
                            failure_context += f"  Suggested fixes: {', '.join(analysis['suggested_fixes'][:2])}\n"
                        if analysis['workflow_changes']:
                            failure_context += f"  Workflow changes needed: {', '.join(analysis['workflow_changes'][:2])}\n"
                failure_context += "\n"
            
            prompt = f"""Fix this GitHub Actions workflow based on actual failure analysis:

{failure_context}Current workflow:
```yaml
{current_content}
```

Please fix the workflow to address the specific failures identified above. Focus on:
1. Resolving the root cause of the identified errors
2. Adding proper error handling and fallbacks
3. Improving robustness to prevent similar failures
4. Maintaining workflow functionality while fixing issues

Output only the corrected YAML content."""
            
            response = self.run_claude_subprocess(prompt, f"fix {workflow_file.name} with failure context")
            
            if response:
                fixed_content = self.extract_yaml_content(response)
                if fixed_content and "name:" in fixed_content:
                    with open(workflow_file, 'w') as f:
                        f.write(fixed_content)
                    return {"status": "success", "file": workflow_file.name, "context": "failure_analysis"}
            
            return {"status": "failed", "file": workflow_file.name, "error": "No valid fix generated"}
                
        except Exception as e:
            return {"status": "error", "file": workflow_file.name, "error": str(e)}
    
    def fix_workflow_basic(self, workflow_file: Path) -> Dict:
        """Basic workflow fix without failure context."""
        try:
            with open(workflow_file, 'r') as f:
                current_content = f.read()
            
            prompt = f"""Analyze and fix common issues in this GitHub Actions workflow:
            
Current workflow:
```yaml
{current_content}
```

Fix these common issues:
- Outdated action versions
- YAML syntax errors
- Missing required dependencies  
- Permission problems
- Broken caching configurations
- Matrix build issues
- Environment variable problems

Output only the fixed YAML content."""
            
            response = self.run_claude_subprocess(prompt, f"basic fix {workflow_file.name}")
            
            if response:
                fixed_content = self.extract_yaml_content(response)
                if fixed_content and "name:" in fixed_content:
                    with open(workflow_file, 'w') as f:
                        f.write(fixed_content)
                    return {"status": "success", "file": workflow_file.name, "context": "basic"}
            
            return {"status": "failed", "file": workflow_file.name, "error": "No valid fix generated"}
                
        except Exception as e:
            return {"status": "error", "file": workflow_file.name, "error": str(e)}
    
    def fix_failing_workflows_intelligently(self) -> bool:
        """Fix workflows using intelligent failure analysis."""
        print("🔨 Intelligent Workflow Failure Analysis & Fixing")
        
        # Get real failure analysis
        failure_analyses = self.analyze_real_failures()
        
        if not failure_analyses:
            print("ℹ️  No recent failures found, performing basic workflow checks...")
            # Fallback to basic fixing
            workflows = self.get_workflow_files()
            if workflows:
                results = []
                for workflow_file in workflows:
                    print(f"🔍 Basic check: {workflow_file.name}")
                    result = self.fix_workflow_basic(workflow_file)
                    results.append(result)
                    
                    if result["status"] == "success":
                        print(f"✅ {result['file']} (basic fixes applied)")
                    else:
                        print(f"❌ {result['file']}: {result.get('error', 'Failed')}")
                
                return len([r for r in results if r["status"] == "success"]) > 0
            return False
        
        print(f"🎯 Found {len(failure_analyses)} workflows with recent failures")
        
        # Group failures by workflow file
        workflow_failures = {}
        for analysis in failure_analyses:
            workflow_name = analysis['workflow_name']
            
            # Find corresponding workflow file
            workflow_file = None
            for ext in ['.yml', '.yaml']:
                potential_file = self.workflows_dir / f"{workflow_name}{ext}"
                if potential_file.exists():
                    workflow_file = potential_file
                    break
            
            if workflow_file:
                if workflow_file not in workflow_failures:
                    workflow_failures[workflow_file] = []
                workflow_failures[workflow_file].append(analysis)
        
        # Fix each workflow with failure context
        results = []
        for workflow_file, analyses in workflow_failures.items():
            print(f"🔧 Fixing {workflow_file.name} based on {len(analyses)} failure(s)")
            
            # Use the most recent failure analysis
            latest_analysis = max(analyses, key=lambda x: x.get('created_at', ''))
            
            result = self.fix_workflow_with_failure_context(workflow_file, latest_analysis)
            results.append(result)
            
            if result["status"] == "success":
                print(f"✅ {result['file']} (fixed based on failure analysis)")
                
                # Show what was fixed
                if latest_analysis.get('job_analyses'):
                    for job_name, job_analysis in latest_analysis['job_analyses'].items():
                        if job_analysis['error_type'] != 'unknown':
                            print(f"   🎯 Addressed: {job_analysis['error_message']}")
            else:
                print(f"❌ {result['file']}: {result.get('error', 'Failed')}")
        
        success_count = len([r for r in results if r["status"] == "success"])
        print(f"\n🎉 Successfully fixed {success_count}/{len(results)} workflows with intelligent analysis")
        
        return success_count > 0
    
    def run_intelligent_analysis(self) -> Dict:
        """Run complete intelligent GitHub Actions analysis with real failure data."""
        print("🤖 Enhanced Claude Agent: GitHub Actions Improver")
        print(f"📁 Repository: {self.repo_path}")
        print("🧠 Using intelligent failure analysis")
        print()
        
        # Detect project information
        project_info = self.detect_project_info()
        print(f"🔍 Project type: {project_info['type']}")
        print(f"🔍 Languages: {', '.join(project_info['languages'])}")
        print(f"🔍 Has tests: {project_info['has_tests']}")
        print(f"🔍 Has workflows: {project_info['has_workflows']}")
        print()
        
        results = {
            "project_info": project_info,
            "failures_analyzed": 0,
            "workflows_fixed": 0,
            "failure_patterns": []
        }
        
        # Intelligent failure analysis and fixing
        if project_info["has_workflows"]:
            print("🔍 Analyzing recent workflow failures...")
            failure_analyses = self.analyze_real_failures()
            results["failures_analyzed"] = len(failure_analyses)
            
            if failure_analyses:
                # Extract failure patterns for reporting
                patterns = set()
                for analysis in failure_analyses:
                    for job_analysis in analysis.get('job_analyses', {}).values():
                        if job_analysis['error_type'] != 'unknown':
                            patterns.add(job_analysis['error_type'])
                results["failure_patterns"] = list(patterns)
                
                print(f"📊 Found failure patterns: {', '.join(patterns)}")
            
            # Fix workflows with intelligent analysis
            if self.fix_failing_workflows_intelligently():
                results["workflows_fixed"] = len(failure_analyses)
        else:
            print("ℹ️  No existing workflows to analyze")
        
        # Summary
        print(f"\n🎉 Intelligent analysis complete!")
        print(f"📊 Failures analyzed: {results['failures_analyzed']}")
        print(f"🔧 Workflows fixed: {results['workflows_fixed']}")
        if results['failure_patterns']:
            print(f"🎯 Patterns addressed: {', '.join(results['failure_patterns'])}")
        
        return results

def main():
    """Main entry point for enhanced GitHub Actions agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Claude Agent: GitHub Actions Improver")
    parser.add_argument("--mode", choices=["analyze", "fix"], default="analyze",
                       help="Operation mode")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    # Verify git repository
    repo_path = Path(args.repo_path)
    if not (repo_path / ".git").exists():
        print("❌ Not a Git repository")
        sys.exit(1)
    
    # Verify Claude CLI
    try:
        subprocess.run(["claude", "--help"], capture_output=True, check=True)
    except:
        print("❌ Claude CLI not available")
        sys.exit(1)
    
    # Verify GitHub CLI for failure analysis
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        print("✅ GitHub CLI available for failure analysis")
    except:
        print("⚠️  GitHub CLI not available - limited failure analysis")
    
    agent = EnhancedGitHubActionsAgent(args.repo_path)
    
    if args.mode == "analyze":
        agent.run_intelligent_analysis()
    elif args.mode == "fix":
        agent.fix_failing_workflows_intelligently()

if __name__ == "__main__":
    main()