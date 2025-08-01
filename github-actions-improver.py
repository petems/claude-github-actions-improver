#!/usr/bin/env python3
"""
Claude Agent for GitHub Actions Improvement

This script analyzes a GitHub repository and:
1. Creates relevant GitHub Actions if none exist
2. Improves existing workflows with DRY principles
3. Fixes failing workflows by spawning specialized agents

Usage: python github-actions-improver.py [--mode create|improve|fix|auto] [--repo-path .]
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class GitHubActionsImprover:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        
    def detect_project_type(self) -> str:
        """Detect the primary project type based on files in the repository."""
        project_indicators = {
            'node': ['package.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
            'rust': ['Cargo.toml'],
            'go': ['go.mod', 'go.sum'],
            'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
            'php': ['composer.json'],
            'ruby': ['Gemfile', 'Rakefile'],
            'dotnet': ['*.csproj', '*.sln', '*.fsproj', '*.vbproj'],
            'docker': ['Dockerfile', 'docker-compose.yml']
        }
        
        detected_types = []
        for project_type, indicators in project_indicators.items():
            for indicator in indicators:
                if list(self.repo_path.glob(indicator)):
                    detected_types.append(project_type)
                    break
        
        # Return the most likely primary type
        if 'node' in detected_types:
            return 'node'
        elif 'python' in detected_types:
            return 'python'
        elif detected_types:
            return detected_types[0]
        else:
            return 'generic'
    
    def has_workflows(self) -> bool:
        """Check if the repository has any GitHub Actions workflows."""
        return self.workflows_dir.exists() and any(self.workflows_dir.glob("*.yml")) or any(self.workflows_dir.glob("*.yaml"))
    
    def get_existing_workflows(self) -> List[Path]:
        """Get list of existing workflow files."""
        if not self.workflows_dir.exists():
            return []
        
        workflows = []
        workflows.extend(self.workflows_dir.glob("*.yml"))
        workflows.extend(self.workflows_dir.glob("*.yaml"))
        return workflows
    
    def run_claude_agent(self, prompt: str, context_files: List[str] = None) -> str:
        """Run Claude CLI with the given prompt and context files."""
        # Build the full prompt with context files content
        full_prompt = prompt
        
        if context_files:
            full_prompt += "\n\nContext files:\n"
            for file_path in context_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        full_prompt += f"\n--- {file_path} ---\n{content}\n"
                    except Exception as e:
                        print(f"Warning: Could not read {file_path}: {e}")
        
        cmd = ["claude", "--print", full_prompt]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode != 0:
                print(f"Claude CLI error: {result.stderr}")
                return ""
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running Claude CLI: {e}")
            return ""
    
    def create_workflows_if_needed(self) -> bool:
        """Create appropriate workflows if none exist."""
        if self.has_workflows():
            print("✅ Workflows already exist, skipping creation")
            return False
        
        project_type = self.detect_project_type()
        print(f"🔍 Detected project type: {project_type}")
        print("🚀 Creating GitHub Actions workflows...")
        
        # Ensure workflows directory exists
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare context files for Claude
        context_files = []
        
        # Add relevant project files as context
        project_files = {
            'node': ['package.json', 'tsconfig.json', 'jest.config.js'],
            'python': ['requirements.txt', 'pyproject.toml', 'setup.py'],
            'rust': ['Cargo.toml'],
            'go': ['go.mod', 'go.sum'],
            'java': ['pom.xml', 'build.gradle']
        }
        
        if project_type in project_files:
            for file in project_files[project_type]:
                file_path = str(self.repo_path / file)
                if os.path.exists(file_path):
                    context_files.append(file_path)
        
        prompt = f"""
        I need you to create appropriate GitHub Actions workflows for a {project_type} project.
        
        Based on the project type and the context files provided, create workflows for:
        
        1. **CI Pipeline** (.github/workflows/ci.yml):
           - Build and test the project
           - Run linting and code quality checks
           - Use appropriate caching strategies
           - Support multiple versions/environments where applicable
        
        2. **Security Scanning** (.github/workflows/security.yml):
           - Dependency vulnerability scanning
           - Code security analysis
           - License compliance checking
        
        3. **Release Automation** (.github/workflows/release.yml) (if applicable):
           - Automated releases on tags
           - Changelog generation
           - Asset building and publishing
        
        Requirements:
        - Use latest stable action versions
        - Implement proper caching for dependencies
        - Use matrix builds where appropriate
        - Include proper error handling
        - Set minimal required permissions
        - Follow security best practices
        - Make workflows efficient and fast
        
        Create the workflow files directly in the .github/workflows/ directory.
        Use conventional naming and ensure they follow GitHub Actions best practices.
        """
        
        response = self.run_claude_agent(prompt, context_files)
        if response:
            print("✅ Workflows created successfully")
            return True
        else:
            print("❌ Failed to create workflows")
            return False
    
    def improve_existing_workflows(self) -> bool:
        """Improve existing workflows with DRY principles and best practices."""
        workflows = self.get_existing_workflows()
        if not workflows:
            print("ℹ️ No existing workflows to improve")
            return False
        
        print(f"🔧 Improving {len(workflows)} existing workflows...")
        
        # Use all workflow files as context
        context_files = [str(w) for w in workflows]
        
        # Also add project files for context
        project_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml']
        for pf in project_files:
            file_path = str(self.repo_path / pf)
            if os.path.exists(file_path):
                context_files.append(file_path)
        
        prompt = """
        Analyze all the GitHub Actions workflows in this repository and improve them by applying DRY (Don't Repeat Yourself) principles and best practices.
        
        Improvements to make:
        
        1. **DRY Improvements**:
           - Extract common steps into composite actions (create in .github/actions/)
           - Create reusable workflows for repeated patterns
           - Consolidate duplicate job configurations
           - Share common environment variables and secrets
        
        2. **Best Practices**:
           - Update all actions to their latest stable versions
           - Add proper caching strategies for dependencies and build artifacts
           - Improve security by pinning action versions to commit SHAs
           - Use minimal required permissions (GITHUB_TOKEN scope)
           - Add better error handling and failure notifications
           - Optimize job dependencies and parallelization
        
        3. **Performance Optimizations**:
           - Remove redundant steps and jobs
           - Improve caching effectiveness
           - Use conditional execution where appropriate
           - Optimize build matrices
        
        4. **Maintainability**:
           - Add clear job and step names
           - Include helpful comments
           - Organize workflows logically
           - Use consistent naming conventions
        
        Please:
        - Maintain backward compatibility
        - Don't break existing functionality
        - Create any necessary composite actions in .github/actions/
        - Update existing workflow files with improvements
        - Ensure all workflows remain functional
        """
        
        response = self.run_claude_agent(prompt, context_files)
        if response:
            print("✅ Workflows improved successfully")
            return True
        else:
            print("❌ Failed to improve workflows")
            return False
    
    def get_failing_workflows(self) -> List[str]:
        """Get list of recently failing workflows from GitHub API or git history."""
        try:
            # Try to get recent workflow runs using GitHub CLI
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "20", "--json", "name,status,conclusion"],
                capture_output=True, text=True, cwd=self.repo_path
            )
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                failing = []
                for run in runs:
                    if run.get("conclusion") == "failure" and run.get("name") not in failing:
                        failing.append(run.get("name"))
                return failing
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        
        # Fallback: assume all workflows might need checking
        workflows = self.get_existing_workflows()
        return [w.stem for w in workflows]
    
    def fix_failing_workflows(self) -> bool:
        """Fix failing workflows by spawning specialized agents for each."""
        failing_workflows = self.get_failing_workflows()
        if not failing_workflows:
            print("✅ No failing workflows detected")
            return True
        
        print(f"🔨 Found {len(failing_workflows)} potentially failing workflows")
        
        success_count = 0
        for workflow_name in failing_workflows:
            print(f"🔍 Analyzing and fixing: {workflow_name}")
            
            # Find the workflow file
            workflow_file = None
            for ext in ['.yml', '.yaml']:
                potential_file = self.workflows_dir / f"{workflow_name}{ext}"
                if potential_file.exists():
                    workflow_file = potential_file
                    break
            
            if not workflow_file:
                print(f"❌ Could not find workflow file for {workflow_name}")
                continue
            
            # Prepare context
            context_files = [str(workflow_file)]
            
            # Add project files for context
            project_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod']
            for pf in project_files:
                file_path = str(self.repo_path / pf)
                if os.path.exists(file_path):
                    context_files.append(file_path)
            
            prompt = f"""
            I need you to analyze and fix issues in the GitHub Actions workflow "{workflow_name}".
            
            Please:
            
            1. **Identify Common Issues**:
               - Outdated action versions
               - Missing or incorrect dependencies
               - Syntax errors in YAML
               - Environment setup problems
               - Permission issues
               - Caching problems
               - Matrix configuration issues
            
            2. **Check Repository Context**:
               - Examine the project structure and dependencies
               - Understand what the workflow is trying to accomplish
               - Verify the build/test commands are correct
            
            3. **Apply Fixes**:
               - Update action versions to latest stable
               - Fix syntax and configuration errors
               - Add missing dependencies or setup steps
               - Correct environment variables and paths
               - Fix permission issues
               - Improve caching configuration
               - Add error handling where needed
            
            4. **Validate**:
               - Ensure the YAML syntax is valid
               - Check that all referenced actions exist
               - Verify the workflow logic makes sense
            
            Please fix the workflow file and explain what issues you found and how you fixed them.
            Focus on making targeted fixes that resolve specific problems without breaking existing functionality.
            """
            
            response = self.run_claude_agent(prompt, context_files)
            if response:
                print(f"✅ Fixed issues in {workflow_name}")
                success_count += 1
            else:
                print(f"❌ Failed to fix {workflow_name}")
        
        print(f"🎉 Successfully fixed {success_count}/{len(failing_workflows)} workflows")
        return success_count > 0
    
    def run(self, mode: str = "auto"):
        """Run the GitHub Actions improver in the specified mode."""
        print(f"🤖 Claude GitHub Actions Improver")
        print(f"📁 Repository: {self.repo_path}")
        print(f"🎯 Mode: {mode}")
        print()
        
        if mode in ["auto", "create"]:
            self.create_workflows_if_needed()
        
        if mode in ["auto", "improve"]:
            self.improve_existing_workflows()
        
        if mode in ["auto", "fix"]:
            self.fix_failing_workflows()
        
        print("\n🎉 GitHub Actions improvement complete!")
        print("\nNext steps:")
        print("- Review the created/modified workflow files")
        print("- Test the workflows by pushing changes or running them manually")
        print("- Commit and push the improvements to your repository")

def main():
    parser = argparse.ArgumentParser(description="Claude Agent for GitHub Actions Improvement")
    parser.add_argument("--mode", choices=["create", "improve", "fix", "auto"], default="auto",
                      help="Operation mode (default: auto)")
    parser.add_argument("--repo-path", default=".", 
                      help="Path to the repository (default: current directory)")
    
    args = parser.parse_args()
    
    # Verify we're in a git repository
    repo_path = Path(args.repo_path).resolve()
    if not (repo_path / ".git").exists():
        print("❌ Error: Not in a Git repository")
        print("Please run this script from within a Git repository or specify --repo-path")
        sys.exit(1)
    
    # Verify Claude CLI is available
    try:
        subprocess.run(["claude", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Claude CLI not found")
        print("Please install Claude CLI: https://docs.anthropic.com/claude/docs")
        sys.exit(1)
    
    improver = GitHubActionsImprover(args.repo_path)
    improver.run(args.mode)

if __name__ == "__main__":
    main()