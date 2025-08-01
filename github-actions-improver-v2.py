#!/usr/bin/env python3
"""
Claude Agent for GitHub Actions Improvement - Streamlined Version

Usage: python github-actions-improver-v2.py [--mode create|improve|fix|auto]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List

class GitHubActionsImprover:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        
    def detect_project_type(self) -> str:
        """Detect the primary project type based on files in the repository."""
        if (self.repo_path / "package.json").exists():
            return "node"
        elif any((self.repo_path / f).exists() for f in ["requirements.txt", "pyproject.toml", "setup.py"]):
            return "python"
        elif (self.repo_path / "Cargo.toml").exists():
            return "rust"
        elif (self.repo_path / "go.mod").exists():
            return "go"
        elif any((self.repo_path / f).exists() for f in ["pom.xml", "build.gradle"]):
            return "java"
        else:
            return "generic"
    
    def has_workflows(self) -> bool:
        """Check if the repository has any GitHub Actions workflows."""
        if not self.workflows_dir.exists():
            return False
        return any(self.workflows_dir.glob("*.yml")) or any(self.workflows_dir.glob("*.yaml"))
    
    def run_claude(self, prompt: str) -> str:
        """Run Claude CLI with the given prompt."""
        cmd = ["claude", "--print", prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode != 0:
                print(f"Claude CLI error: {result.stderr}")
                return ""
            return result.stdout
        except Exception as e:
            print(f"Error running Claude CLI: {e}")
            return ""
    
    def extract_yaml_from_response(self, response: str) -> str:
        """Extract YAML content from Claude's response."""
        if "```yaml" in response:
            return response.split("```yaml")[1].split("```")[0].strip()
        elif "```" in response:
            return response.split("```")[1].split("```")[0].strip()
        return response.strip()
    
    def create_workflows_if_needed(self) -> bool:
        """Create appropriate workflows if none exist."""
        if self.has_workflows():
            print("✅ Workflows already exist, skipping creation")
            return False
        
        project_type = self.detect_project_type()
        print(f"🔍 Detected project type: {project_type}")
        print("🚀 Creating GitHub Actions workflows...")
        
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Create CI workflow
        if project_type == "python":
            prompt = """Create a GitHub Actions CI workflow for a Python project.
            Include: Python 3.8-3.11 matrix, pip caching, pytest, flake8.
            Output only the YAML content."""
        elif project_type == "node":
            prompt = """Create a GitHub Actions CI workflow for a Node.js project.
            Include: Node 16,18,20 matrix, npm caching, npm test, npm run lint.
            Output only the YAML content."""
        elif project_type == "rust":
            prompt = """Create a GitHub Actions CI workflow for a Rust project.
            Include: cargo build, cargo test, cargo clippy, proper caching.
            Output only the YAML content."""
        elif project_type == "go":
            prompt = """Create a GitHub Actions CI workflow for a Go project.
            Include: Go 1.19-1.21 matrix, go build, go test, go vet.
            Output only the YAML content."""
        else:
            prompt = """Create a basic GitHub Actions CI workflow.
            Include: checkout, basic build/test steps.
            Output only the YAML content."""
        
        response = self.run_claude(prompt)
        if response:
            yaml_content = self.extract_yaml_from_response(response)
            ci_file = self.workflows_dir / "ci.yml"
            with open(ci_file, 'w') as f:
                f.write(yaml_content)
            print(f"✅ Created {ci_file}")
            return True
        else:
            print("❌ Failed to create CI workflow")
            return False
    
    def improve_existing_workflows(self) -> bool:
        """Improve existing workflows with best practices."""
        if not self.has_workflows():
            print("ℹ️ No existing workflows to improve")
            return False
        
        workflows = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        print(f"🔧 Improving {len(workflows)} existing workflows...")
        
        for workflow_file in workflows:
            print(f"🔍 Improving: {workflow_file.name}")
            
            with open(workflow_file, 'r') as f:
                current_content = f.read()
            
            prompt = f"""Improve this GitHub Actions workflow with best practices:
            - Update action versions to latest
            - Add proper caching
            - Improve security and permissions
            - Optimize performance
            
            Current workflow:
            ```yaml
            {current_content}
            ```
            
            Output only the improved YAML content."""
            
            response = self.run_claude(prompt)
            if response:
                improved_content = self.extract_yaml_from_response(response)
                with open(workflow_file, 'w') as f:
                    f.write(improved_content)
                print(f"✅ Improved {workflow_file.name}")
            else:
                print(f"❌ Failed to improve {workflow_file.name}")
        
        return True
    
    def fix_failing_workflows(self) -> bool:
        """Fix common issues in workflows."""
        if not self.has_workflows():
            print("ℹ️ No workflows to fix")
            return False
        
        workflows = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        print(f"🔨 Checking {len(workflows)} workflows for common issues...")
        
        for workflow_file in workflows:
            print(f"🔍 Analyzing: {workflow_file.name}")
            
            with open(workflow_file, 'r') as f:
                current_content = f.read()
            
            prompt = f"""Analyze and fix common issues in this GitHub Actions workflow:
            - Outdated action versions
            - Syntax errors
            - Missing dependencies
            - Permission issues
            - Caching problems
            
            Current workflow:
            ```yaml
            {current_content}
            ```
            
            Output only the fixed YAML content."""
            
            response = self.run_claude(prompt)
            if response:
                fixed_content = self.extract_yaml_from_response(response)
                with open(workflow_file, 'w') as f:
                    f.write(fixed_content)
                print(f"✅ Fixed {workflow_file.name}")
            else:
                print(f"❌ Failed to fix {workflow_file.name}")
        
        return True
    
    def run(self, mode: str = "auto"):
        """Run the GitHub Actions improver in the specified mode."""
        print(f"🤖 Claude GitHub Actions Improver v2")
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

def main():
    parser = argparse.ArgumentParser(description="Claude Agent for GitHub Actions Improvement")
    parser.add_argument("--mode", choices=["create", "improve", "fix", "auto"], default="auto")
    args = parser.parse_args()
    
    # Verify we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a Git repository")
        sys.exit(1)
    
    # Verify Claude CLI is available
    try:
        subprocess.run(["claude", "--help"], capture_output=True, check=True)
    except:
        print("❌ Error: Claude CLI not found")
        sys.exit(1)
    
    improver = GitHubActionsImprover()
    improver.run(args.mode)

if __name__ == "__main__":
    main()